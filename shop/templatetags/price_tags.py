from decimal import Decimal, ROUND_HALF_UP
from django import template
from django.utils.html import format_html
from django.conf import settings

register = template.Library()


@register.filter
def display_price(value):
    """Format price without thousands separator and without unnecessary decimals.

    Examples:
    - 120.00 -> '120'
    - 89.99  -> '89.99'
    - 1000.5 -> '1000.5'
    """
    if value is None:
        return ''
    try:
        d = Decimal(value)
    except Exception:
        try:
            d = Decimal(str(value))
        except Exception:
            return value

    # If whole number, return integer form
    if d == d.quantize(Decimal('1')):
        return str(d.quantize(Decimal('1')))

    # Otherwise keep up to 2 decimal places, trim trailing zeros
    q = d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    # normalize then format without scientific notation
    s = format(q.normalize(), 'f')
    return s


@register.simple_tag
def price_html(value, old_value=None, size='text-2xl'):
    """Affichage de prix 100% unifié dans tout le site : même police (Montserrat),
    même taille exacte, et 'FCFA' toujours dans la même police/taille/couleur que le chiffre.
    Affiche automatiquement le prix barré si old_value est fourni et supérieur à value.
    """
    currency = getattr(settings, 'DEFAULT_CURRENCY', 'FCFA')
    formatted = display_price(value)

    old_html = ''
    if old_value:
        try:
            if Decimal(str(old_value)) > Decimal(str(value)):
                old_formatted = display_price(old_value)
                old_html = format_html(
                    '<span class="price-old">{} {}</span>',
                    old_formatted, currency
                )
        except Exception:
            pass

    return format_html(
        '{}<span class="price-display {}">{}<span class="price-currency">{}</span></span>',
        old_html, size, formatted, currency
    )
