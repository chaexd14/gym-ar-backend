from django.db import models
from django.contrib.auth.models import User

class WorkoutSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='workout_sessions')
    username = models.CharField(max_length=100, default='Athlete', db_index=True)
    exercise = models.CharField(max_length=100, default='Bodyweight Squats')
    total_reps = models.IntegerField(default=0)
    good_reps = models.IntegerField(default=0)
    perfect_reps = models.IntegerField(default=0)
    flagged_reps = models.IntegerField(default=0)
    accuracy_rate = models.FloatField(default=0.0)
    average_score = models.FloatField(default=0.0)
    start_time = models.BigIntegerField(null=True, blank=True, help_text="Timestamp in ms")
    end_time = models.BigIntegerField(null=True, blank=True, help_text="Timestamp in ms")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} - {self.exercise} - {self.total_reps} reps ({self.accuracy_rate}%)"


class RepDetail(models.Model):
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='rep_history')
    rep_number = models.IntegerField()
    is_good = models.BooleanField(default=True)
    is_perfect = models.BooleanField(default=False)
    score = models.FloatField(default=100.0)
    lowest_score = models.FloatField(default=100.0)
    min_knee_angle = models.FloatField(help_text="Lowest knee angle in degrees")
    duration_ms = models.IntegerField(default=0, help_text="Rep duration in ms")
    issues = models.JSONField(default=list, blank=True, help_text="List of detected form issues")
    snapshot_image = models.TextField(blank=True, null=True, help_text="Base64 snapshot of mistake / lowest score")
    snapshot_reason = models.CharField(max_length=200, blank=True, null=True)
    snapshot_angle = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ['rep_number']

    def __str__(self):
        status = "Perfect" if self.is_perfect else ("Good" if self.is_good else "Flagged")
        return f"Rep #{self.rep_number} ({status}) - {self.min_knee_angle}°"
