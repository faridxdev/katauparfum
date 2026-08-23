from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_productnote_product_associated_products'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductFAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255, verbose_name='Question')),
                ('answer', models.TextField(verbose_name='Réponse')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Ordre')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faqs', to='shop.product')),
            ],
            options={
                'verbose_name': 'FAQ produit',
                'verbose_name_plural': 'FAQ produit',
                'ordering': ['order', 'id'],
            },
        ),
    ]
