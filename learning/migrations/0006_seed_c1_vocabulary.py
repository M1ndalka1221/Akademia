# Data migration to seed initial C1 level Polish-Russian vocabulary items into the database

from django.db import migrations


def seed_c1_vocabulary(apps, schema_editor):
    Vocabulary = apps.get_model("learning", "Vocabulary")

    vocabulary_data = [
        {
            "word": "zawiłość",
            "translation": "сложность / запутанность",
            "example_sentence": "Należy szczegółowo przeanalizować prawną zawiłość tej kwestii przed podjęciem decyzji."
        },
        {
            "word": "skrupulatność",
            "translation": "тщательность / скрупулезность",
            "example_sentence": "Jego skrupulatność w weryfikacji danych pozwoliła uniknąć poważnych błędów."
        },
        {
            "word": "ubolewać",
            "translation": "сожалеть / сокрушаться",
            "example_sentence": "Wielu ekspertów ubolewa nad spadkiem czytelnictwa wśród młodego pokolenia."
        },
        {
            "word": "nacechowany",
            "translation": "окрашенный / охарактеризованный",
            "example_sentence": "Artykuł był silnie nacechowany emocjonalnie, co wpłynęło na jego obiektywizm."
        },
        {
            "word": "rozwiać wątpliwości",
            "translation": "развеять сомнения",
            "example_sentence": "Przedstawione dowody całkowicie rozwiały wątpliwości członków komisji."
        },
        {
            "word": "wzbudzać kontrowersje",
            "translation": "вызывать разногласия / споры",
            "example_sentence": "Nowa reforma edukacji od samego początku wzbudzała ogromne kontrowersje."
        },
        {
            "word": "przedsięwzięcie",
            "translation": "инициатива / проект / мероприятие",
            "example_sentence": "Organizowanie międzynarodowego festiwalu to złożone i odpowiedzialne przedsięwzięcie."
        },
        {
            "word": "skłaniać do refleksji",
            "translation": "побуждать к размышлениям",
            "example_sentence": "Przeczytana powieść skłania do głębokiej refleksji nad sensownością ludzkich wyborów."
        }
    ]

    for data in vocabulary_data:
        Vocabulary.objects.get_or_create(
            word=data["word"],
            defaults={
                "translation": data["translation"],
                "example_sentence": data["example_sentence"],
                "level": "C1",
                "is_custom": False,
            }
        )


def reverse_seed_c1_vocabulary(apps, schema_editor):
    Vocabulary = apps.get_model("learning", "Vocabulary")
    Vocabulary.objects.filter(is_custom=False).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0005_vocabulary_level_is_custom_user"),
    ]

    operations = [
        migrations.RunPython(seed_c1_vocabulary, reverse_code=reverse_seed_c1_vocabulary),
    ]
