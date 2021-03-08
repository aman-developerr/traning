from django.db import models
from django.contrib.auth.models import User


class Routine(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    today_date = models.DateField(max_length=20)
    check_in_times = models.TimeField(max_length=20, null=True)
    in_location = models.CharField(max_length=80, null=True)
    in_ip = models.CharField(max_length=30, null=True)
    check_out_time = models.TimeField(max_length=20, null=True)
    out_location = models.CharField(max_length=80, null=True)
    out_ip = models.CharField(max_length=20, null=True)
    current_project = models.CharField(max_length=30, null=True)
    billable_task = models.TextField(null=True)
    break_time = models.TextField(max_length=20, null=True)
    task_owner = models.CharField(max_length=30, null=True)
    approved_by = models.CharField(max_length=30, null=True)
