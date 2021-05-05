from django.contrib import admin

# Register your models here.
from .models import Question, Answer, Poll, StudentAnswer, MyUser

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Poll)
admin.site.register(StudentAnswer)
admin.site.register(MyUser)
