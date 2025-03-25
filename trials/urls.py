# backend/trials/urls.py
from django.urls import path
from .views import TrialListView, TrialMeView, TrialDetailView, TrialReportView

urlpatterns = [
    path('trials/', TrialListView.as_view(), name='trials-list'),
    path('trials/me', TrialMeView.as_view(), name='trial-me'),
    path('trials/<int:id>', TrialDetailView.as_view(), name='trials-detail'),
    path('trials/<int:id>/report', TrialReportView.as_view(), name='trials-report'),

]