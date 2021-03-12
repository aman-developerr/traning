from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('profile/<int:pk>/', views.user_profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),
    path('today/', views.today, name='today'),
    path('t/', views.test),
    path('edit_routine/<int:pk>/', views.edit_routine, name='edit_routine'),
    path('trainee/', views.trainee, name='trainee'),
    path('trainee_details/<int:pk>/', views.trainee_details, name='trainee_details'),
    path('notifications/<int:pk>/', views.notifications, name='notifications'),
    # path('check_in/', views.check_in, name='check_in'),
]
