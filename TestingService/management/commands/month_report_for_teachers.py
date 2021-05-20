import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.template.loader import render_to_string

from TestingService.models import MyUser, Poll


class Command(BaseCommand):

    def handle(self, *args, **options):
        current_date = datetime.date.today()
        last_month = current_date - datetime.timedelta(days=30)

        obj = [set(Poll.objects.filter(question__answer__studentanswer__created_at__gte=last_month,
                                       question__answer__studentanswer__student__in=MyUser.objects.filter(
                                           is_teacher=False)))]
        polls_count = 0    # Получаем количество пройденных тестов студентами
        for polls in obj:
            polls_count += len(polls)

        teachers_list = []
        for teacher in MyUser.objects.filter(is_teacher=True):   # Получаем список всех учителей кому отсылать отчет
            teachers_list.append(teacher.email)

        msg = render_to_string('month_report_for_teachers.html', {'obj': polls_count})
        send_mail('Ежемесячный отчет о количестве пройденных тестов',
                  msg,
                  settings.EMAIL_HOST_USER,
                  teachers_list,
                  html_message=msg)
