# filepath: backend/templates/emails.py
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from trials.models import Trial
from users.models import User
import re
from rest_framework_simplejwt.tokens import AccessToken

WEBSITE_URL = settings.WEBSITE_URL

def send_email(subject, content, to):
    from_email=f"eKapituła HKK <{settings.EMAIL_HOST_USER}>"
    body = f"""
        Czuwaj!
        {content}

        Wiadomość wygenerowana automatycznie przez system eKapituła HKK
    """
    html_content = f"""
        <!DOCTYPE html>
        <html lang="pl">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <meta http-equiv="Content-Language" content="pl">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;700&display=swap');
                
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    padding: 30px;
                    font-family: 'Rubik', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, sans-serif;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #2c3e50;
                    padding-bottom: 20px;
                }}
                .logo {{
                    max-width: 150px;
                }}
                .content {{
                    padding: 30px 0;
                    line-height: 1.6;
                    color: #34495e;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #193cb8;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 9999px;
                    margin: 20px 0;
                }}
                .button:hover {{
                    background-color: #1c398e;
                }}
                .footer {{
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 0.9em;
                    border-top: 2px solid #ecf0f1;
                    padding-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://lubelskie.zhr.pl/wp-content/uploads/2018/10/logo_ZHR_z_napisem_na_znaku-1-e1539176777246.png" alt="Logo HKK" class="logo">
                    <h1>Czuwaj!</h1>
                </div>
                
                <div class="content">
                    {content}                
                </div>
                
                <div class="footer">
                    <p>Wiadomość wygenerowana automatycznie przez system eKapituła HKK</p>
                </div>
            </div>
        </body>
        </html>
    """    
    email = EmailMultiAlternatives(subject, body, from_email, to, headers={
            'Content-Type': 'text/html; charset=UTF-8',
            'Content-Language': 'pl-PL',
        } )
    email.attach_alternative(html_content, "text/html")
    email.send()   
    

def reqest_mentor_check(trial_id):
    trial = Trial.objects.get(id=trial_id)    
    subject = "Zostałeś poproszony o sprawdzenie próby"
    content = f"""
    <p><strong>{trial.user.full_name}</strong> poprosił Cię o sprawdzenie swojej próby.</p>                
        <center>
            <a href="{WEBSITE_URL}/proba/{trial_id}" class="button">
                Przejdź do próby
            </a>
        </center>
    """
    send_email(subject, content, {trial.mentor_mail})

def approve_trial_mentor(trial_id):
    trial = Trial.objects.get(id=trial_id)
    mentor_name = User.objects.get(login=trial.mentor_mail).full_name
    subject = "Twoja próba została zaakceptowana"
    content = f"""
    <p><strong>{mentor_name}</strong> <span style="color: green;">zaakceptował</span> twoją próbę. Teraz możesz umówić się na spotkanie z kapitułą.</p>                
        <center>
            <a href="{WEBSITE_URL}" class="button">
                Przejdź do próby
            </a>
        </center>
    """
    send_email(subject, content, {trial.email})

def leave_trial_mentor(trial_id):
    trial = Trial.objects.get(id=trial_id)
    subject = "Twój opiekun porzucił twoją próbę"
    content = f"""
    <p>Twój opiekun <span style="color: red;">porzucił</span> twoją próbę. Dodaj nowego opiekuna na stronie próby.</p>                
        <center>
            <a href="{WEBSITE_URL}" class="button">
                Przejdź do próby
            </a>
        </center>
    """
    send_email(subject, content, {trial.email})

def sign_up_for_meeting(trial_id):
    trial = Trial.objects.get(id=trial_id)
    trial_status = trial.status
    status = ""
    if "Otwarta" in trial_status:
        status = ". Jego próba ma status otwarta"
        if "edytowano" in trial_status:
            status += " (edytowana)"
    elif "zaakceptowana przez opiekuna" in trial_status:
        status = ". Jego próba ma status do otwarcia"  

    subject = "Nowe zgłoszenie na kapitułę"
    content = f"""
    <p><strong>{trial.user.full_name}</strong> (<a href="mailto:{trial.email}">{trial.email}</a>) zgłosił się na kapitułę{status}. Zobacz jego próbę:</p>                
        <center>
            <a href="{WEBSITE_URL}/proba/{trial_id}" class="button">
                Przejdź do próby
            </a>
        </center>
    """
    send_email(subject, content, {admin.login for admin in User.objects.filter(role="Administrator")} )

def approve_trial_open(trial_id):
    trial = Trial.objects.get(id=trial_id)
    subject = "Twoja próba została zatwierdzona przez kapitułę"
    content = f"""
    <p>Twoja próba została <span style="color: green;">zatwierdzona</span> przez kapitułę i przekazana do otwarcia w rozkazie przez hufcowego.</p>                
        <center>
            <a href="{WEBSITE_URL}" class="button">
                Przejdź do próby
            </a>
        </center>
    """
    send_email(subject, content, {trial.email})

def reject_trial(trial_id):
    trial = Trial.objects.get(id=trial_id)
    subject = "Twoja próba została odrzucona przez kapitułę"
    content = f"""
    <p>Twoja próba została <span style="color: red;">odrzucona</span> przez kapitułę. Popraw ją wraz z opiekunem i umów się ponownie na spotkanie.</p>                
        <center>
            <a href="{WEBSITE_URL}" class="button">
                Przejdź do próby
            </a>
        </center>
    """
    send_email(subject, content, {trial.email})

def open_trial(trial_id):
    trial = Trial.objects.get(id=trial_id)

    # Wyrażenie regularne do wyodrębnienia numeru rozkazu i linku
    match = re.match(r"^(Otwarta rozkazem) ([^<]+) <(.+?)>(.*)$", trial.status)
    if match:
        _, orderNumber, orderLink, _ = match.groups()
    else:
        orderNumber = ""
        orderLink = ""

    subject = "Twoja próba została otwarta"
    content = f"""
    <p>Twoja próba została otwarta przez hufcowego rozkazem {orderNumber}.</p>                
        <center>
            <a href="{orderLink}" class="button">
                Zobacz rozkaz
            </a>
        </center>
    """
    send_email(subject, content, {trial.email})

def approve_trial_close(trial_id):
    trial = Trial.objects.get(id=trial_id)
    subject = "Twoja próba została zatwierdzona kapitułę"
    content = f"""
    <p>Twoja próba została <span style="color: green;">zatwierdzona</span> przez kapitułę i przekazana do zamknięcia w rozkazie przez hufcowego.</p>                
        <center>
            <a href="{WEBSITE_URL}" class="button">
                Przejdź do próby
            </a>
        </center>
    """
    send_email(subject, content, {trial.email})

def close_trial(trial_id):
    trial = Trial.objects.get(id=trial_id)

    # Wyrażenie regularne do wyodrębnienia numeru rozkazu i linku
    match = re.match(r"^(Zamknięta rozkazem) ([^<]+) <(.+?)>(.*)$", trial.status)
    if match:
        _, orderNumber, orderLink, _ = match.groups()
    else:
        orderNumber = ""
        orderLink = ""

    subject = "Twoja próba została zamknięta"
    content = f"""
    <p>Twoja próba została zamknięta przez hufcowego rozkazem {orderNumber}. Gratulacje!</p>                
        <center>
            <a href="{orderLink}" class="button">
                Zobacz rozkaz
            </a>
        </center>
    """
    send_email(subject, content, {trial.email})

####### ACCOUNT EMAILS #######

import uuid

def send_verification_email(user_id):
    user = User.objects.get(id=user_id)
    user.verified = str(uuid.uuid4())
    user.save()
    subject = "Potwierdzenie rejestracji"
    content = f"""
    <p>Witaj {user.full_name},</p>
    <p>Dziękujemy za rejestrację. Kliknij poniższy przycisk, aby potwierdzić swój adres email:</p>
    <center>
        <a href="{WEBSITE_URL}/weryfikacja/{user.id}/{user.verified}" class="button">
            Potwierdź email
        </a>
    </center>
    """
    send_email(subject, content, {user.login})