from django.contrib import admin
from .models import Routine,Feedback,Profile,FeedbackRequest


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','file']

@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'today_date', 'check_in_times','in_ip','in_location', 'check_out_time','out_ip','out_location', 'current_project', 'billable_task', 'break_time', 'task_owner','approved_by']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'feedback_time', 'feedback','trainer']

@admin.register(FeedbackRequest)
class FeedbackRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'request_time', 'feedback_request','trainer']
