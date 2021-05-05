from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from TestingService import views
from TestingService.forms import LoginForm

urlpatterns = [
    path('', views.ListPolls.as_view(), name='ListPolls'),
    path('<int:pk>/', views.ListQuestions.as_view(), name='ListQuestions'),
    path('question/<int:pk>/', views.ListAnswers.as_view(), name='ListAnswers'),
    path('result/', views.ResultPollsStudent.as_view(), name='ResultForStudent'),
    path('registration/', views.registration_user, name='registration_user'),
    path('login/', views.LoginViewAnonUser.as_view(template_name='login.html', authentication_form=LoginForm), name='LoginViewAnonUser'),
    path('studentpolls/', views.DetailStudent.as_view(), name='DetailStudent'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
