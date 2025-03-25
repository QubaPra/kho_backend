from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .emails import *

class EmailFunctionView(APIView):
    def post(self, request, *args, **kwargs):
        function = request.data.get('function')
        trial_id = request.data.get('trial_id')

        if not function or not trial_id:
            return Response({'error': 'Brak wymaganych parametrów'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Wywołaj funkcję dynamicznie
            function = globals()[function]
            function(trial_id)
            return Response({'message': 'Sent'}, status=status.HTTP_200_OK)
        except KeyError:
            return Response({'error': 'Unknown function'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)