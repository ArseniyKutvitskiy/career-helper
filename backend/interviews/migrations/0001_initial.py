from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name="InterviewSession", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("role", models.CharField(max_length=160)), ("vacancy_description", models.TextField(blank=True)),
        ("question", models.TextField()), ("answer", models.TextField(blank=True)),
        ("score", models.PositiveSmallIntegerField(blank=True, null=True)),
        ("feedback", models.JSONField(blank=True, default=dict)), ("created_at", models.DateTimeField(auto_now_add=True)),
    ], options={"ordering": ["-created_at"]})]
