from django.db import migrations


FAQ_ENTRIES = [
    (
        'Ces parfums durent-ils longtemps?',
        "La tenue dépend de la peau et de la météo, mais nos formules sont pensées pour laisser un sillage présent pendant de longues heures.",
    ),
    (
        "J'ai vu un bouchon doré sur vos photos, mais le mien est argenté. Est-ce normal ?",
        "Oui, c'est normal. Le bouchon argenté et le flacon dégradé correspondent à nos commandes pour l'Europe. Le modèle doré apparaît parfois dans des visuels destinés à d'autres régions, mais le parfum reste exactement le même.",
    ),
    (
        'Quelque chose vous fait hésiter? Posez-nous vos questions!',
        'Notre équipe est disponible pour vous guider et répondre à toutes vos questions avant votre commande.',
    ),
]


def add_default_faqs(apps, schema_editor):
    Product = apps.get_model('shop', 'Product')
    ProductFAQ = apps.get_model('shop', 'ProductFAQ')
    for product in Product.objects.all():
        for order, (question, answer) in enumerate(FAQ_ENTRIES):
            ProductFAQ.objects.get_or_create(
                product=product,
                question=question,
                defaults={'answer': answer, 'order': order},
            )


def remove_default_faqs(apps, schema_editor):
    ProductFAQ = apps.get_model('shop', 'ProductFAQ')
    ProductFAQ.objects.filter(question__in=[question for question, _ in FAQ_ENTRIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_productfaq'),
    ]

    operations = [
        migrations.RunPython(add_default_faqs, remove_default_faqs),
    ]
