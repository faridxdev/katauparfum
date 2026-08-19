from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, Category


class ProductSitemap(Sitemap):
    """Toutes les fiches produit disponibles : la partie la plus importante du sitemap,
    ce sont ces pages qui doivent apparaître dans les résultats Google."""
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_available=True)

    def location(self, obj):
        return reverse('shop:product_detail', args=[obj.slug])

    def lastmod(self, obj):
        return obj.created_at


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return f"{reverse('shop:products')}?category={obj.slug}"


class StaticViewSitemap(Sitemap):
    """Pages statiques du site (accueil, boutique)"""
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return ['shop:home', 'shop:products']

    def location(self, item):
        return reverse(item)
