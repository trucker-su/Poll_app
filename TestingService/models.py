from django.conf import settings
from django.contrib.auth.models import User, AbstractUser
from django.db import models


# Create your models here.


class Poll(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Question(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.CharField(max_length=50)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=50)
    is_correct = models.BooleanField()

    def __str__(self):
        return self.answer_text


class MyUser(AbstractUser):
    is_teacher = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class StudentAnswer(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.answer.question.text
