from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('create/', views.quiz_create, name='quiz_create'),
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<int:quiz_id>/edit/', views.quiz_edit, name='quiz_edit'),
    path('<int:quiz_id>/delete/', views.quiz_delete, name='quiz_delete'),
    path('<int:quiz_id>/question/add/', views.question_create, name='question_create'),
    path('<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('submission/<int:submission_id>/', views.take_quiz, name='take_quiz'),
    path('submission/<int:submission_id>/result/', views.quiz_result, name='quiz_result'),
]