from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("interviews", "0001_initial"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField(model_name="interviewsession", name="mode", field=models.CharField(default="technical", max_length=40)),
        migrations.AddField(model_name="interviewsession", name="user", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="interview_sessions", to=settings.AUTH_USER_MODEL)),
    ]
