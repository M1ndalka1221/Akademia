# Data migration to seed initial AI essay topics into the database

from django.db import migrations


def seed_ai_topics(apps, schema_editor):
    Topic = apps.get_model("learning", "Topic")

    topics_data = [
        {
            "title": "Rola sztucznej inteligencji w edukacji przyszłości",
            "description": "Przedstaw swoje stanowisko na temat wpływu rozwoju narzędzi AI na tradycyjny system nauczania i rolę nauczyciela w szkołach wyższych."
        },
        {
            "title": "Wpływ mediów społecznościowych na relacje międzyludzkie",
            "description": "Zanalizuj plusy i minusy komunikacji cyfrowej. Czy wirtualne sieci zbliżają czy oddalają ludzi od siebie w codziennym życiu?"
        },
        {
            "title": "Wyzwania ochrony środowiska w XXI wieku",
            "description": "Omów najważniejsze wyzwania ekologiczne współczesnego świata oraz zaproponuj działania, jakie jednostki i państwa powinny podjąć."
        },
        {
            "title": "Kultura i tradycja a nowoczesność w globalnym świecie",
            "description": "Jak zachować tożsamość kulturową i narodowe tradycje w dobie globalizacji i szybkiego postępu technologicznego?"
        },
        {
            "title": "Etyka w sztuce i literaturze współczesnej",
            "description": "Gdzie leży granica wolności wypowiedzi artystycznej? Przeanalizuj problem odpowiedzialności społecznej twórców w XXI wieku."
        }
    ]

    for data in topics_data:
        Topic.objects.get_or_create(
            title=data["title"],
            defaults={
                "description": data["description"],
                "is_custom": False,
            }
        )


def reverse_seed_ai_topics(apps, schema_editor):
    Topic = apps.get_model("learning", "Topic")
    Topic.objects.filter(is_custom=False).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0003_essay_user_topic_user"),
    ]

    operations = [
        migrations.RunPython(seed_ai_topics, reverse_code=reverse_seed_ai_topics),
    ]
