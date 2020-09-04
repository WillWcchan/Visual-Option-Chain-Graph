from celery import shared_task
from django.core.mail import send_mail
from time import sleep

# Start the worker process and be on top of the mysite directory: celery -A mysite worker -l info -E

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
