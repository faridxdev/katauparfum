from django.contrib import admin
from .models import Category, Product, ProductImage, Order, OrderItem, Review, QuantityDiscountRule, SiteSettings, NewsletterSubscriber


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at']
    search_fields = ['email']
    ordering = ['-subscribed_at']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Réglages globaux du site (singleton) : vidéo hero, photos genre de la page d'accueil, etc."""
    list_display = ['__str__']

    fieldsets = (
        ('🎬 Vidéo de fond (page d\'accueil)', {
            'fields': ('hero_video', 'hero_video_url'),
        }),
        ('🚻 Photos "Achetez Par Genre" (page d\'accueil)', {
            'fields': ('gender_image_women', 'gender_image_men', 'gender_image_unisex'),
            'description': "Une photo par bloc (Femme / Homme / Unisexe). Format portrait recommandé. Si vide, une image générique est utilisée à la place.",
        }),
    )

    def has_add_permission(self, request):
        # Empêche de créer plusieurs enregistrements (singleton)
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'gender']
    list_filter = ['gender']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class ProductImageInline(admin.TabularInline):
    """Permet d'ajouter plusieurs images (galerie) directement depuis la fiche produit"""
    model = ProductImage
    extra = 3
    fields = ['image', 'order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'gender', 'price', 'old_price',
        'is_bestseller', 'is_new', 'is_available', 'created_at'
    ]
    list_filter = ['is_available', 'category', 'gender', 'scent_family', 'is_bestseller', 'is_new', 'created_at']
    search_fields = ['name', 'description', 'inspired_by']
    readonly_fields = ['created_at', 'image_preview']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

    def image_preview(self, obj):
        """Affiche une prévisualisation de l'image"""
        if obj.image:
            from django.utils.html import format_html
            return format_html(
                '<img src="{}" style="max-width: 250px; max-height: 250px; border-radius: 8px; box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2); border: 2px solid #d4af37;" />',
                obj.image.url
            )
        return "✨ Aucune image"

    image_preview.short_description = "👁️ Aperçu"

    fieldsets = (
        ('🎁 Informations Produit', {
            'fields': ('name', 'slug', 'category', 'gender', 'price', 'old_price', 'is_available')
        }),
        ('🏷️ Badges Marketing', {
            'fields': ('is_bestseller', 'is_new'),
        }),
        ('📸 Description & Image Principale', {
            'fields': ('description', 'image', 'image_preview')
        }),
        ('🌸 Profil Olfactif', {
            'fields': (
                'scent_family', 'intensity', 'concentration', 'concentration_percent',
                'volume_ml', 'top_notes', 'heart_notes', 'base_notes', 'ingredients_highlight',
            )
        }),
        ('💎 Inspiration Luxe', {
            'fields': ('inspired_by', 'luxury_price_reference'),
            'description': "Ces champs affichent sur la fiche produit : « Inspiré de X » et « Y FCFA moins cher que la version originale »."
        }),
        ('📅 Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(QuantityDiscountRule)
class QuantityDiscountRuleAdmin(admin.ModelAdmin):
    list_display = ['min_quantity', 'discount_percent', 'is_active']
    list_editable = ['discount_percent', 'is_active']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']
    can_delete = False
    fields = ['product', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'delivery_date', 'total_price', 'created_at']
    list_filter = ['delivery_date', 'created_at']
    search_fields = ['full_name', 'phone', 'address']
    readonly_fields = ['created_at', 'get_whatsapp_link']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('👤 Informations Client', {
            'fields': ('full_name', 'phone', 'address')
        }),
        ('🚚 Détails Livraison', {
            'fields': ('delivery_date', 'total_price')
        }),
        ('💬 Notification WhatsApp', {
            'fields': ('get_whatsapp_link',),
            'classes': ('collapse',)
        }),
        ('⏰ Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_whatsapp_link(self, obj):
        """Affiche le lien WhatsApp pour contacter le client"""
        import urllib.parse
        message = obj.get_whatsapp_message()
        whatsapp_url = f"https://wa.me/{obj.phone}?text={urllib.parse.quote(message)}"
        return f'<a href="{whatsapp_url}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #25D366 0%, #128c7e 100%); color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 700; box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3);">📱 Contacter sur WhatsApp</a>'
    
    get_whatsapp_link.short_description = '📱 WhatsApp'
    get_whatsapp_link.allow_tags = True


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'author', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'product']
    search_fields = ['author', 'text', 'product__name']
