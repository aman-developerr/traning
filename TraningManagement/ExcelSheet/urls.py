from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve


urlpatterns = [
    path('', views.user_login, name='login'),
    path('dashboard/<int:pk>/', views.user_dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('today/', views.today, name='today'),
    path('t/', views.test),
    path('edit_routine/<int:pk>/', views.edit_routine, name='edit_routine'),
    path('trainee/', views.trainee, name='trainee'),
    path('trainee_details/<int:pk>/', views.trainee_details, name='trainee_details'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('notifications/<int:pk>/', views.notifications, name='notifications'),
    path('feedback/', views.feedback, name='feedback'),
    path('feedbackadd_add/', views.feedback_add, name='feedback_add'),
    url(r'^download/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
