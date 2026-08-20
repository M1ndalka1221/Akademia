from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("learning", "0004_seed_ai_topics"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="vocabulary",
            options={"ordering": ["-created_at", "word"], "verbose_name": "Vocabulary", "verbose_name_plural": "Vocabularies"},
        ),
        migrations.AddField(
            model_name="vocabulary",
            name="is_custom",
            field=models.BooleanField(default=False, help_text="Designates whether this word was created manually by a user."),
        ),
        migrations.AddField(
            model_name="vocabulary",
            name="level",
            field=models.CharField(default="C1", help_text="CEFR proficiency level (e.g., C1).", max_length=10),
        ),
        migrations.AddField(
            model_name="vocabulary",
            name="user",
            field=models.ForeignKey(blank=True, help_text="User who saved this vocabulary item (null for AI/system defaults).", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="vocabularies", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="vocabulary",
            name="example_sentence",
            field=models.TextField(blank=True, help_text="Example sentence illustrating usage in Polish."),
        ),
        migrations.AlterField(
            model_name="vocabulary",
            name="translation",
            field=models.CharField(help_text="Russian translation of the word.", max_length=255),
        ),
        migrations.AlterField(
            model_name="vocabulary",
            name="word",
            field=models.CharField(help_text="The Polish C1 word or phrase.", max_length=255),
        ),
    ]
