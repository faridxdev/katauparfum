from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_seed_product_faq'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='site_favicon',
            field=models.ImageField(
                blank=True,
                help_text='Petite image carrée, idéalement 32x32 ou 64x64 pixels (PNG, JPG ou ICO).',
                null=True,
                upload_to='site/',
                verbose_name='Favicon du site',
            ),
        ),
    ]
