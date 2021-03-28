from django.db import models
from django.contrib.auth.models import User


class Routine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    today_date = models.DateField(max_length=20)
    check_in_times = models.TimeField(max_length=20, null=True)
    in_location = models.CharField(max_length=150, null=True)
    in_ip = models.CharField(max_length=30, null=True)
    check_out_time = models.TimeField(max_length=20, null=True)
    out_location = models.CharField(max_length=150, null=True)
    out_ip = models.CharField(max_length=20, null=True)
    current_project = models.CharField(max_length=30, null=True, default='Pending')
    billable_task = models.TextField(null=True, default='Pending')
    break_time = models.TextField(max_length=50, null=True, default='Pending')
    task_owner = models.CharField(max_length=30, null=True, default='Pending')
    approved_by = models.CharField(max_length=30, null=True, default='Pending')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='media/', max_length=255, blank=True)


class FeedbackRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trainer = models.CharField(max_length=30 ,null=True)
    feedback_request = models.BooleanField(default=False)
    request_time = models.DateTimeField(max_length=30)


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trainer = models.CharField(max_length=30, null=True)
    feedback = models.TextField(max_length=100, null=True)
    feedback_time = models.DateTimeField(max_length=20)
