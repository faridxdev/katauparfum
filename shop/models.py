from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import logging
try:
    from cloudinary_storage.storage import VideoMediaCloudinaryStorage
except Exception:
    VideoMediaCloudinaryStorage = None
from django.utils.text import slugify
from PIL import Image


GENDER_CHOICES = [
    ('women', 'Femme'),
    ('men', 'Homme'),
    ('unisex', 'Unisexe'),
]

SCENT_FAMILY_CHOICES = [
    ('floral', 'Fleuri'),
    ('fresh', 'Frais'),
    ('gourmand', 'Gourmand'),
    ('herbal', 'Herbacé'),
    ('earthy', 'Terreux'),
    ('warm', 'Chaud'),
]

INTENSITY_CHOICES = [
    ('soft', 'Douce'),
    ('significant', 'Significative'),
    ('statement', 'Affirmée'),
]

CONCENTRATION_CHOICES = [
    ('edp', 'Eau de Parfum'),
    ('edt', 'Eau de Toilette'),
    ('oil', 'Huile de Parfum'),
    ('extrait', 'Extrait de Parfum'),
]


class Category(models.Model):
    """Catégorie de produits (Parfum / Huile de parfum)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, default='unisex',
        verbose_name="Genre principal",
        help_text="Utilisé pour les blocs 'Shop by Gender' de la page d'accueil"
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Produits (parfums et huiles de parfum)"""
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        verbose_name="Ancien prix (barré)",
        help_text="Laisser vide si le produit n'est pas en promotion"
    )
    image = models.ImageField(upload_to='products/', verbose_name="Image principale")
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # --- Informations olfactives (inspiré de dossier.eu) ---
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex', verbose_name="Genre")
    scent_family = models.CharField(
        max_length=20, choices=SCENT_FAMILY_CHOICES, blank=True, null=True,
        verbose_name="Famille olfactive"
    )
    intensity = models.CharField(
        max_length=15, choices=INTENSITY_CHOICES, blank=True, null=True,
        verbose_name="Intensité du parfum"
    )
    concentration = models.CharField(
        max_length=10, choices=CONCENTRATION_CHOICES, default='edp',
        verbose_name="Concentration"
    )
    concentration_percent = models.CharField(
        max_length=20, blank=True, null=True,
        verbose_name="% de concentration", help_text="Ex: 18%"
    )
    volume_ml = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Contenance (ml)"
    )

    top_notes = models.CharField(max_length=255, blank=True, null=True, verbose_name="Notes de tête")
    heart_notes = models.CharField(max_length=255, blank=True, null=True, verbose_name="Notes de cœur")
    base_notes = models.CharField(max_length=255, blank=True, null=True, verbose_name="Notes de fond")
    associated_products = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='associated_with',
        verbose_name="Produits à associer",
        help_text="Seuls ces produits apparaîtront dans la section « À associer »."
    )
    ingredients_highlight = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Ingrédients clés",
        help_text="Ex: Vegan, Cruelty-free, Sans paraben"
    )

    inspired_by = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name="Inspiré de (marque de luxe)",
        help_text="Ex: Baccarat Rouge 540 - Maison Francis Kurkdjian"
    )
    luxury_price_reference = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        verbose_name="Prix de la marque de luxe équivalente",
        help_text="Sert à calculer l'économie affichée sur la fiche produit"
    )

    # --- Badges marketing ---
    is_bestseller = models.BooleanField(default=False, verbose_name="Badge Bestseller")
    is_new = models.BooleanField(default=False, verbose_name="Badge Nouveauté")

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_available', 'category']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug_candidate = base_slug
            i = 1
            while Product.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                i += 1
                slug_candidate = f"{base_slug}-{i}"
            self.slug = slug_candidate

        """Redimensionne et compresse l'image automatiquement à la sauvegarde"""
        super().save(*args, **kwargs)

        if self.image:
            try:
                img = Image.open(self.image.path)
                # Si l'image est plus grande que 1200px, on la réduit (Qualité Luxe HD)
                if img.height > 1200 or img.width > 1200:
                    output_size = (1200, 1200)
                    img.thumbnail(output_size)
                    # Sauvegarde optimisée (qualité 85%)
                    img.save(self.image.path, quality=85, optimize=True)
            except Exception:
                pass  # On ignore les erreurs si le fichier n'est pas accessible

    @property
    def discount_percent(self):
        """Pourcentage de réduction si old_price est défini"""
        if self.old_price and self.old_price > self.price:
            return round((1 - (self.price / self.old_price)) * 100)
        return 0

    @property
    def savings_vs_luxury(self):
        """Économie réalisée par rapport à la référence de luxe"""
        if self.luxury_price_reference and self.luxury_price_reference > self.price:
            return self.luxury_price_reference - self.price
        return None

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def average_rating_rounded(self):
        return round(self.average_rating)

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def gallery_images(self):
        """Toutes les images secondaires, dans l'ordre"""
        return self.images.all().order_by('order')


class ProductImage(models.Model):
    """Images supplémentaires pour la galerie d'une fiche produit"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        ordering = ['order']
        verbose_name = "Image de galerie"
        verbose_name_plural = "Images de galerie"

    def __str__(self):
        return f"Image {self.order} - {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            try:
                img = Image.open(self.image.path)
                if img.height > 1200 or img.width > 1200:
                    img.thumbnail((1200, 1200))
                    img.save(self.image.path, quality=85, optimize=True)
            except Exception:
                pass


class ProductNote(models.Model):
    """Note olfactive illustrée affichée dans la fiche produit."""
    NOTE_TYPES = [
        ('top', 'Tête'),
        ('heart', 'Cœur'),
        ('base', 'Fond'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='note_items')
    note_type = models.CharField(max_length=10, choices=NOTE_TYPES, verbose_name="Étape")
    name = models.CharField(max_length=100, verbose_name="Nom de la note")
    image = models.ImageField(upload_to='products/notes/', blank=True, null=True, verbose_name="Image de la note")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        ordering = ['note_type', 'order', 'name']
        verbose_name = "Note olfactive illustrée"
        verbose_name_plural = "Notes olfactives illustrées"

    def __str__(self):
        return f"{self.get_note_type_display()} - {self.name} ({self.product.name})"


class ProductFAQ(models.Model):
    """Question et réponse FAQ propres à un produit."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=255, verbose_name="Question")
    answer = models.TextField(verbose_name="Réponse")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "FAQ produit"
        verbose_name_plural = "FAQ produit"

    def __str__(self):
        return f"{self.question} ({self.product.name})"


class SiteSettings(models.Model):
    """Réglages globaux du site, modifiables depuis l'admin sans toucher au code.
    Un seul enregistrement existe (singleton)."""
    hero_video = models.FileField(
        upload_to='site/', blank=True, null=True,
        verbose_name="Vidéo de fond (page d'accueil)",
        help_text="Format MP4 recommandé, quelques secondes en boucle, poids léger (< 10 Mo idéalement).",
        storage=(
            VideoMediaCloudinaryStorage()
            if VideoMediaCloudinaryStorage is not None and settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
            else FileSystemStorage()
        ),
    )
    hero_video_url = models.URLField(
        blank=True, null=True,
        verbose_name="OU lien vidéo externe (Cloudinary, YouTube-mp4, etc.)",
        help_text="Si rempli, prioritaire sur le fichier uploadé ci-dessus."
    )

    # --- Photos des blocs "Shop by Gender" sur la page d'accueil ---
    gender_image_women = models.ImageField(
        upload_to='site/', blank=True, null=True,
        verbose_name="Photo bloc Femme",
        help_text="Format portrait recommandé (ratio 3:4). Si vide, une image générique est utilisée."
    )
    gender_image_men = models.ImageField(
        upload_to='site/', blank=True, null=True,
        verbose_name="Photo bloc Homme",
        help_text="Format portrait recommandé (ratio 3:4). Si vide, une image générique est utilisée."
    )
    gender_image_unisex = models.ImageField(
        upload_to='site/', blank=True, null=True,
        verbose_name="Photo bloc Unisexe",
        help_text="Format portrait recommandé (ratio 3:4). Si vide, une image générique est utilisée."
    )
    site_favicon = models.ImageField(
        upload_to='site/', blank=True, null=True,
        verbose_name="Favicon du site",
        help_text="Petite image carrée, idéalement 32x32 ou 64x64 pixels (PNG, JPG ou ICO)."
    )

    class Meta:
        verbose_name = "Réglages du site"
        verbose_name_plural = "Réglages du site"

    def __str__(self):
        return "Réglages du site KATAUPARFUM"

    @property
    def resolved_hero_video_url(self):
        if self.hero_video_url:
            return self.hero_video_url
        if self.hero_video:
            return self.hero_video.url
        return None

    def save(self, *args, **kwargs):
        self.pk = 1  # force singleton
        try:
            super().save(*args, **kwargs)
        except Exception:
            logging.exception('Error saving SiteSettings')
            raise

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class NewsletterSubscriber(models.Model):
    """Inscriptions à la newsletter (section 'Soyez la première informée' du footer)"""
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = "Inscrit newsletter"
        verbose_name_plural = "Inscrits newsletter"

    def __str__(self):
        return self.email


class QuantityDiscountRule(models.Model):
    """Règle de réduction automatique par quantité totale d'articles dans le panier
    (ex: 3 articles = -10%, 4 = -15%, 5 = -20%, comme dossier.eu)"""
    min_quantity = models.PositiveIntegerField(unique=True, verbose_name="Quantité minimum d'articles")
    discount_percent = models.PositiveIntegerField(verbose_name="Réduction (%)")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['min_quantity']
        verbose_name = "Règle de réduction par quantité"
        verbose_name_plural = "Règles de réduction par quantité"

    def __str__(self):
        return f"{self.min_quantity}+ articles = -{self.discount_percent}%"


class Order(models.Model):
    """Commande du client"""
    DELIVERY_CHOICES = [
        ('today', 'Aujourd\'hui'),
        ('tomorrow', 'Demain'),
    ]

    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)  # Numéro WhatsApp
    address = models.TextField()
    delivery_date = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    subtotal_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percent = models.PositiveIntegerField(default=0, verbose_name="Réduction quantité appliquée (%)")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande #{self.id} - {self.full_name}"

    def get_whatsapp_message(self):
        """Génère le message WhatsApp pour la commande"""
        items_text = "\n".join([
            f"• {item.product.name} × {item.quantity} - {item.price} FCFA"
            for item in self.orderitem_set.all()
        ])
        
        delivery_text = "Aujourd'hui" if self.delivery_date == 'today' else "Demain"

        discount_line = ""
        if self.discount_percent:
            discount_line = f"\n*Sous-total:* {self.subtotal_price} FCFA\n*Réduction quantité:* -{self.discount_percent}%"

        message = f"""*Nouvelle Commande KATAUPARFUM*

*Client:* {self.full_name}
*Téléphone:* {self.phone}
*Adresse:* {self.address}

*Produits:*
{items_text}
{discount_line}
*Total:* {self.total_price} FCFA
*Livraison:* {delivery_text}

Commande ID: #{self.id}"""
        
        return message


class OrderItem(models.Model):
    """Ligne d'une commande"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order', 'product')

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"


class Review(models.Model):
    """Avis clients sur les produits"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    author = models.CharField(max_length=100, verbose_name="Nom du client")
    rating = models.PositiveSmallIntegerField(default=5, verbose_name="Note (1-5)")
    text = models.TextField(verbose_name="Commentaire")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author} sur {self.product.name} ({self.rating}/5)"
