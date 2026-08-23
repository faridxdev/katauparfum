# Generated manually for the product detail fragrance profile and associations.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_alter_category_id_alter_newslettersubscriber_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='associated_products',
            field=models.ManyToManyField(
                blank=True,
                related_name='associated_with',
                symmetrical=False,
                to='shop.product',
                verbose_name='Produits à associer',
                help_text='Seuls ces produits apparaîtront dans la section « À associer ».',
            ),
        ),
        migrations.CreateModel(
            name='ProductNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note_type', models.CharField(choices=[('top', 'Tête'), ('heart', 'Cœur'), ('base', 'Fond')], max_length=10, verbose_name='Étape')),
                ('name', models.CharField(max_length=100, verbose_name='Nom de la note')),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/notes/', verbose_name='Image de la note')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Ordre')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='note_items', to='shop.product')),
            ],
            options={
                'verbose_name': 'Note olfactive illustrée',
                'verbose_name_plural': 'Notes olfactives illustrées',
                'ordering': ['note_type', 'order', 'name'],
            },
        ),
    ]
