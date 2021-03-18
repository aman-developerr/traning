from django.contrib import admin
from .models import Routine,Feedback,Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','profile_image',]

@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'today_date', 'check_in_times','in_ip','in_location', 'check_out_time','out_ip','out_location', 'current_project', 'billable_task', 'break_time', 'task_owner','approved_by']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'feedback_time', 'feedback']
