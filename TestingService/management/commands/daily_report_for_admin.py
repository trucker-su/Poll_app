from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.template.loader import render_to_string

from TestingService.models import StudentAnswer, MyUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        obj = StudentAnswer.objects.filter(created_at=datetime.now())
        admin_email = []
        for user in MyUser.objects.filter(is_superuser=True):
            admin_email.append(user.email)
        spisok_polls = []
        for studentanswer in obj:
            spisok_polls.append(studentanswer.answer.question.poll)
        msg = render_to_string('daily_report_for_admin.html', {'obj': set(spisok_polls)})
        send_mail('Ежедневный отчет о пройденных тестах',
                  msg,
                  settings.EMAIL_HOST_USER,
                  admin_email,
                  html_message=msg)
