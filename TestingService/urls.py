from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.forms import AuthenticationForm
from django.urls import path

from TestingService import views


urlpatterns = [
    path('', views.ListPolls.as_view(), name='ListPolls'),
    path('<int:pk>/', views.ListQuestions.as_view(), name='ListQuestions'),
    path('question/<int:pk>/', views.ListAnswers.as_view(), name='ListAnswers'),
    path('result/', views.ResultPollsStudent.as_view(), name='ResultForStudent'),
    path('registration/', views.registration_user, name='registration_user'),
    path('login/', views.LoginViewAnonUser.as_view(template_name='login.html', authentication_form=AuthenticationForm),
         name='LoginViewAnonUser'),
    path('studentpolls/', views.ListStudent.as_view(), name='ListStudent'),
    path('studentpolls/users/<int:pk>/', views.DetailStudentPollsResult.as_view(),
         name='DetailStudentPollsResult'),
    path('studentpolls/users/<int:pk_2>/poll/<int:pk_1>/', views.result_student_poll, name='result_student_poll'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
