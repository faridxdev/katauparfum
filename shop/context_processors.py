from django.conf import settings


def site_settings(request):
    """Expose les réglages globaux (dont la vidéo hero et les photos genre) dans tous les templates"""
    from .models import SiteSettings
    try:
        settings_obj = SiteSettings.load()
        video_url = settings_obj.resolved_hero_video_url
        gender_women_url = settings_obj.gender_image_women.url if settings_obj.gender_image_women else None
        gender_men_url = settings_obj.gender_image_men.url if settings_obj.gender_image_men else None
        gender_unisex_url = settings_obj.gender_image_unisex.url if settings_obj.gender_image_unisex else None
        favicon_url = settings_obj.site_favicon.url if settings_obj.site_favicon else None
    except Exception:
        video_url = None
        gender_women_url = gender_men_url = gender_unisex_url = None
        favicon_url = None
    return {
        'HERO_VIDEO_URL': video_url,
        'GENDER_IMAGE_WOMEN': gender_women_url,
        'GENDER_IMAGE_MEN': gender_men_url,
        'GENDER_IMAGE_UNISEX': gender_unisex_url,
        'SITE_FAVICON_URL': favicon_url,
    }


def currency(request):
    """Expose la devise utilisée dans les templates"""
    return {
        'CURRENCY': getattr(settings, 'DEFAULT_CURRENCY', 'FCFA')
    }


def whatsapp_config(request):
    """Expose le numéro WhatsApp admin dans les templates"""
    return {
        'WHATSAPP_ADMIN_PHONE': getattr(settings, 'WHATSAPP_ADMIN_PHONE', '+33XXXXXXXXX')
    }
