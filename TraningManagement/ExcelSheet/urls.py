from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('profile/<int:pk>/', views.user_profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),
    path('today/', views.today, name='today'),
    path('t/', views.test),
    path('edit_routine/<int:pk>/', views.edit_routine, name='edit_routine'),
    # path('check_in/', views.check_in, name='check_in'),
]
