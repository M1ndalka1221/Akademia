"""Management command to seed initial Polish essay topics for Akademia."""

from django.core.management.base import BaseCommand
from learning.models import Topic


class Command(BaseCommand):
    help = "Seed initial C1 Polish essay topics"

    def handle(self, *args, **options) -> None:
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
                "title": "Wywania ochrony środowiska w XXI wieku",
                "description": "Omów najważniejsze wyzwania ekologiczne współczesnego świata oraz zaproponuj działania, jakie jednostki i państwa powinny podjąć."
            },
            {
                "title": "Kultura i tradycja a nowoczesność",
                "description": "Jak zachować tożsamość kulturową i narodowe tradycje w dobie globalizacji i szybkiego postępu technologicznego?"
            }
        ]

        created_count = 0
        for data in topics_data:
            _, created = Topic.objects.get_or_create(
                title=data["title"],
                defaults={"description": data["description"]}
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Pomyślnie załadowano {created_count} nowych tematów esejów!")
        )
