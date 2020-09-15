from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime
from time import sleep

# Start the worker process and be on top of the visual-option-chain directory: celery -A visual-option-chain worker -l info -E

@shared_task
def send_email_task(subject, message, from_email, recipient_list):
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False,
    )
    return None

@shared_task
def display_time():
    print("The time is %s :" % str(datetime.now()))
    return True
