from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse

from django.views.generic import ListView, DetailView

from TestingService.forms import RegistrationForm, LoginForm
from TestingService.models import Poll, Question, Answer, StudentAnswer, MyUser


class ListPolls(LoginRequiredMixin, ListView):
    """Отображение списка тестов для студента"""
    template_name = 'index.html'
    context_object_name = 'list_polls'
    login_url = 'LoginViewAnonUser'

    def get_queryset(self):
        if not self.request.user.is_teacher:
            obj = Poll.objects.all()
            return obj
        obj = []
        return obj

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            return super().get(request, *args, **kwargs)
        return redirect('DetailStudent')


class ListQuestions(LoginRequiredMixin, DetailView):
    """ Отображение списка вопросов для студента"""
    template_name = 'detail.html'
    login_url = 'LoginViewAnonUser'

    def get_queryset(self):
        if not self.request.user.is_teacher:
            obj = Poll.objects.all()
            return obj
        raise Http404


class ListAnswers(LoginRequiredMixin, DetailView):
    """Тест с вариантами ответов для студента"""
    template_name = 'detail_answers.html'
    model = Question
    login_url = 'LoginViewAnonUser'

    def get_queryset(self):
        if not self.request.user.is_teacher:
            obj = Question.objects.all()
            return obj
        raise Http404

    def post(self, request, *args, **kwargs):
        selected_answer = request.POST.get('ans', )
        if selected_answer:
            if not self.model.objects.filter(answer__studentanswer__student=request.user, text=Answer.objects.get(
                    answer_text=selected_answer).question.text).exists():
                otvet = StudentAnswer.objects.create(answer=Answer.objects.get(answer_text=selected_answer),
                                                     student=request.user, votes=0)
                otvet.save()
                if otvet.answer.is_correct:
                    otvet.votes = 1
                    otvet.save()
                    self.extra_context = {'message': 'Ваш ответ принят, перейдите обратно к списку вопросов, чтобы '
                                                     'выбрать '
                                                     'следующий'}
                    return self.get(request, *args, **kwargs)
                self.extra_context = {'message': 'Ваш ответ принят, перейдите обратно к списку вопросов, чтобы выбрать '
                                                 'следующий'}
                return self.get(request, *args, **kwargs)
            self.extra_context = {'message': 'Вы уже ответили на этот вопрос выберите другой'}
            return self.get(request, *args, **kwargs)
        self.extra_context = {'message': 'Выберите один из вариантов'}
        return self.get(request, *args, **kwargs)


class ResultPollsStudent(LoginRequiredMixin, ListView):
    """Результаты пройденных тестов для конкретного студента, отображается статистика только для самого себя"""
    template_name = 'studentsresult.html'
    login_url = 'LoginViewAnonUser'

    def get_queryset(self):
        if not self.request.user.is_teacher:
            obj = Answer.objects.filter(studentanswer__student=self.request.user)  # думал добавить
            # UserPassesTestMixin, но из-за этой строки смысла не вижу
            if obj:
                return obj

            self.extra_context = {'message': 'Вы не прошли ни одного теста'}
            return self.get
        raise Http404

    def get_context_data(self, **kwargs):
        context = super(ResultPollsStudent, self).get_context_data(**kwargs)
        context['answers'] = self.get_queryset()
        context['testi'] = set(Poll.objects.filter(question__answer__studentanswer__student=self.request.user))
        context['voprosi'] = Question.objects.filter(answer__studentanswer__student=self.request.user)
        context['tets'] = {}
        for i in context['testi']:
            context['tets'][i] = len(
                StudentAnswer.objects.filter(votes=1, student=self.request.user, answer__question__poll=i))
        context['all_answers_for_student_question'] = Answer.objects.filter()
        return context


def registration_user(request):
    """Регистрация новых пользователей"""
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                is_teacher = form.cleaned_data.get('is_teacher')
                new_user = MyUser.objects.create_user(username=username, password=password, is_teacher=is_teacher)
                if not new_user.is_teacher:
                    authenticate(new_user)
                    login(request, new_user)
                    return redirect('ListPolls')
                authenticate(new_user)
                login(request, new_user)
                return HttpResponse('Надо редирект на главную если учитель')
            message = form.errors
            form = RegistrationForm()
            return render(request, 'registration.html', {'message': message, 'form': form})
        form = RegistrationForm()
        return render(request, 'registration.html', {'form': form})
    raise Http404


class LoginViewAnonUser(LoginView):
    """Авторизация пользователей"""
    form_class = LoginForm
    redirect_authenticated_user = '/'

    def form_valid(self, form):
        is_teacher = form.cleaned_data.get('is_teacher')
        return super(LoginViewAnonUser, self).form_valid(form)


class DetailStudent(LoginRequiredMixin, ListView):
    """Просмотр результатов студентов для учителя"""
    template_name = 'result_for_teacher.html'
    model = MyUser

    def get_context_data(self, **kwargs):
        context = super(DetailStudent, self).get_context_data(**kwargs)
        context['students'] = self.model.objects.filter(is_teacher=False)
        poll_point = {}
        for i in context['students']:
            poll_point[i] = {}
            for m in Poll.objects.filter(question__answer__studentanswer__student__username=i):
                poll_point[i][m] = len(StudentAnswer.objects.filter(votes=1, student=i, answer__question__poll=m))
        context['poll_point'] = poll_point
        return context

