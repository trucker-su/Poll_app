
from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from django.views.generic import ListView, DetailView

from TestingService.forms import RegistrationForm
from TestingService.models import Poll, Question, Answer, StudentAnswer, MyUser


class PermissionForStudents(PermissionRequiredMixin):

    def has_permission(self):
        return not self.request.user.is_teacher


class PermissionForTeachers(PermissionRequiredMixin):

    def has_permission(self):
        return self.request.user.is_teacher


class ListPolls(LoginRequiredMixin, PermissionForStudents, ListView):
    """Отображение списка тестов для студента"""
    template_name = 'index.html'
    context_object_name = 'list_polls'
    login_url = 'LoginViewAnonUser'
    model = Poll


class ListQuestions(LoginRequiredMixin, PermissionForStudents, DetailView):
    """ Отображение списка вопросов для студента"""
    template_name = 'detail.html'
    login_url = 'LoginViewAnonUser'
    model = Poll


class ListAnswers(LoginRequiredMixin, PermissionForStudents, DetailView):
    """Тест с вариантами ответов для студента"""
    template_name = 'detail_answers.html'
    model = Question
    login_url = 'LoginViewAnonUser'

    def post(self, request, *args, **kwargs):
        selected_answer = request.POST.get('ans', )
        if selected_answer:
            if not StudentAnswer.objects.filter(student=request.user, answer__question=self.get_object()).exists():
                otvet = StudentAnswer.objects.create(answer=Answer.objects.get(answer_text=selected_answer,
                                                                               question=self.get_object()),
                                                     student=request.user,
                                                     votes=0)
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


class ResultPollsStudent(LoginRequiredMixin, PermissionForStudents, ListView):
    """Результаты пройденных тестов для конкретного студента, отображается статистика только для самого себя"""
    template_name = 'studentsresult.html'
    login_url = 'LoginViewAnonUser'

    def get_queryset(self):
        obj = Answer.objects.filter(studentanswer__student=self.request.user)
        if obj:
            return obj
        self.extra_context = {'message': 'Вы не прошли ни одного теста'}
        return self.get

    def get_context_data(self, **kwargs):
        context = super(ResultPollsStudent, self).get_context_data(**kwargs)
        context['answers'] = self.get_queryset()
        context['tests'] = set(Poll.objects.filter(question__answer__studentanswer__student=self.request.user))
        context['voprosi'] = Question.objects.filter(answer__studentanswer__student=self.request.user)
        context['test_point'] = {}
        for test in context['tests']:
            context['test_point'][test] = StudentAnswer.objects.filter(votes=1,
                                                                       student=self.request.user,
                                                                       answer__question__poll=test).count()
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
                return redirect('ListStudent')
            message = form.errors
            form = RegistrationForm()
            return render(request, 'registration.html', {'message': message, 'form': form})
        form = RegistrationForm()
        return render(request, 'registration.html', {'form': form})
    raise PermissionDenied


class LoginViewAnonUser(LoginView, LoginRequiredMixin):
    """Авторизация пользователей"""
    form_class = AuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        is_teacher = form.user_cache.is_teacher
        if is_teacher:
            login(self.request, form.get_user())
            return HttpResponseRedirect('/studentpolls/')
        login(self.request, form.get_user())
        return HttpResponseRedirect('/')


class ListStudent(LoginRequiredMixin, PermissionForTeachers, ListView):
    """Просмотр результатов студентов для учителя"""
    template_name = 'result_for_teacher.html'
    queryset = MyUser.objects.filter(is_teacher=False)
    context_object_name = 'all_students'


class DetailStudentPollsResult(LoginRequiredMixin, PermissionForTeachers, DetailView):
    template_name = 'everypollresultforstudent.html'
    model = MyUser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        polls = set(Poll.objects.filter(question__answer__studentanswer__student=self.object))
        context['polls'] = {}
        for poll in polls:
            context['polls'][poll] = StudentAnswer.objects.filter(answer__question__poll=poll,
                                                                  student=self.object,
                                                                  answer__is_correct=True).count()

        return context


def teacher_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_teacher,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


@teacher_required
def result_student_poll(request, pk_1, pk_2):
    """Просмотр результатов студента (кол-во баллов, правильные и неправильные ответы, вопросы)"""
    poll = get_object_or_404(Poll, pk=pk_1)
    stud = get_object_or_404(MyUser, pk=pk_2)
    questions = Question.objects.filter(poll=poll, answer__studentanswer__student=stud)
    student_answer = StudentAnswer.objects.filter(answer__question__poll=poll, student=stud)
    correct_answers = Answer.objects.filter(is_correct=True, question__poll=poll, studentanswer__student=stud)
    if request.method == 'POST':
        StudentAnswer.objects.filter(answer__question__poll=poll, student=stud).delete()
    return render(request, 'detail_polls_result_with_answers.html', {'poll': poll,
                                                                     'stud': stud,
                                                                     'questions': questions,
                                                                     'student_answer': student_answer,
                                                                     'correct_answers': correct_answers,
                                                                     })
