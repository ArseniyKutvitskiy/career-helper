from django.db import models

class InterviewSession(models.Model):
    user = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.CASCADE, related_name="interview_sessions")
    role = models.CharField(max_length=160)
    mode = models.CharField(max_length=40, default="technical")
    vacancy_description = models.TextField(blank=True)
    question = models.TextField()
    answer = models.TextField(blank=True)
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.role}: {self.question[:50]}"
