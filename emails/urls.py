from django.urls import path
from emails.views import EmailFunctionView

urlpatterns = [
    path('emails', EmailFunctionView.as_view(), name='email_function'),
]