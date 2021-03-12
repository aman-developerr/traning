from django.contrib import admin
from .models import Routine


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'today_date', 'check_in_times','in_ip','in_location', 'check_out_time','out_ip','out_location', 'current_project', 'billable_task', 'break_time', 'task_owner','approved_by']
