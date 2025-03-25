# backend/trials/views.py
from rest_framework import generics
from .models import Trial
from .serializers import TrialSerializer, TrialListSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class TrialListView(generics.ListAPIView):
    queryset = Trial.objects.all()
    serializer_class = TrialListSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        self.queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TrialMeView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    serializer_class = TrialSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Trial.objects.get(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TrialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trial.objects.all()
    serializer_class = TrialSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'



################### GOOGLE DRIVE API REPORTS ###################


# Zakres dostępu (modyfikuj według potrzeb)
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8090)  # Stały port
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def find_folder_id(service, folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])
    if not folders:
        raise Exception(f"Folder '{folder_name}' nie istnieje.")
    return folders[0]['id']  # Zakładamy, że istnieje tylko jeden folder o tej nazwie

def find_file_in_folder(service, folder_id, file_name):
    query = f"'{folder_id}' in parents and name='{file_name}' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    if not files:
        raise Exception(f"Plik '{file_name}' nie istnieje w folderze.")
    return files[0]['id']

def check_if_file_exists(service, folder_id, file_name):
    query = f"'{folder_id}' in parents and name='{file_name}' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return files[0] if files else None

def copy_and_share_file(service, original_file_id, new_name):
    # Utwórz kopię pliku
    copied_file = service.files().copy(
        fileId=original_file_id,
        body={'name': new_name}
    ).execute()

    # Udostępnij wszystkim do edycji
    permission = {
        'type': 'anyone',
        'role': 'writer',
        'allowFileDiscovery': False
    }
    service.permissions().create(
        fileId=copied_file['id'],
        body=permission
    ).execute()

    # Zwróć URL
    return f"https://docs.google.com/document/d/{copied_file['id']}"

class TrialReportView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)
        trial_id = kwargs.get('id')

        try:
            # Znajdź folder "Raporty"
            folder_id = find_folder_id(service, "Raporty")

            # Znajdź plik "Szablon raportu HO" w folderze
            file_id = find_file_in_folder(service, folder_id, "Szablon raportu HO.docx")

            # Utwórz nazwę kopii z datą
            new_name = f"Raport końcowy HO {trial_id}"

            # Sprawdź, czy plik już istnieje
            existing_file = check_if_file_exists(service, folder_id, new_name)
            if existing_file:
                existing_url = f"https://docs.google.com/document/d/{existing_file['id']}"
                trial = Trial.objects.get(id=trial_id)
                trial.report = existing_url
                trial.save()
                return JsonResponse({'message': existing_url})
            else:
                # Skopiuj i udostępnij plik
                url = copy_and_share_file(service, file_id, new_name)
                trial = Trial.objects.get(id=trial_id)
                trial.report = url
                trial.save()
                return JsonResponse({'message': url})

        except HttpError as error:
            return JsonResponse({'error': str(error)}, status=500)