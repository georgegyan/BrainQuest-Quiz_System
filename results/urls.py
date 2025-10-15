from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('submissions/', views.submission_history, name='submission_history'),
    path('submissions/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('quiz/<int:quiz_id>/analytics/', views.quiz_analytics, name='quiz_analytics'),
]