from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.conf import settings
from django.contrib import messages
import urllib.parse
import json
from decimal import Decimal

from .models import Category, Product, Order, OrderItem, Review, QuantityDiscountRule, NewsletterSubscriber


def get_cart_from_session(request):
    """Récupère le panier de la session"""
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']


def save_cart_to_session(request, cart):
    """Enregistre le panier dans la session"""
    request.session['cart'] = cart
    request.session.modified = True


def calculate_cart_total(cart):
    """Calcule le total du panier"""
    total = Decimal('0.00')
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            total += product.price * quantity
        except Product.DoesNotExist:
            continue
    return total


def get_quantity_discount(total_items_count):
    """Retourne le meilleur % de réduction applicable selon la quantité totale d'articles
    dans le panier (règles définies dans l'admin, ex: 3+ = -10%, 4+ = -15%, 5+ = -20%)."""
    rule = (
        QuantityDiscountRule.objects
        .filter(is_active=True, min_quantity__lte=total_items_count)
        .order_by('-min_quantity')
        .first()
    )
    return rule.discount_percent if rule else 0


def home(request):
    """Page d'accueil avec les produits vedettes"""
    categories = Category.objects.all()
    # Limite stricte : Affiche uniquement les 6 derniers produits sur l'accueil
    products = Product.objects.filter(is_available=True).select_related('category').order_by('-created_at')[:6]
    cart = get_cart_from_session(request)
    cart_count = sum(cart.values())
    
    context = {
        'categories': categories,
        'products': products,
        'cart_count': cart_count,
    }
    return render(request, 'home.html', context)


def products(request):
    """Listing de tous les produits avec filtrage par catégorie"""
    categories = Category.objects.all()
    category_slug = request.GET.get('category', None)
    product_id = request.GET.get('product_id', None)
    query = request.GET.get('q', '').strip()
    gender_filter = request.GET.get('gender', None)
    scent_family_filter = request.GET.get('scent_family', None)
    sort = request.GET.get('sort', None)
    
    # Traitement du formulaire d'avis (POST)
    if request.method == 'POST' and 'submit_review' in request.POST:
        try:
            r_product_id = request.POST.get('product_id')
            r_author = request.POST.get('author')
            r_rating = request.POST.get('rating')
            r_text = request.POST.get('text')
            
            if r_product_id and r_author and r_rating and r_text:
                prod = get_object_or_404(Product, id=r_product_id)
                Review.objects.create(product=prod, author=r_author, rating=int(r_rating), text=r_text)
                messages.success(request, "Merci ! Votre avis a été ajouté avec succès. 💎")
                return redirect(f"{request.path}?product_id={r_product_id}")
        except Exception as e:
            messages.error(request, "Une erreur est survenue lors de l'ajout de l'avis.")

    # Logique d'affichage normale (GET)
    products_qs = Product.objects.filter(is_available=True)

    # Liste complète pour la sidebar (A-Z)
    all_products_sidebar = Product.objects.filter(is_available=True).order_by('name')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products_qs = products_qs.filter(category=category)
        selected_category = category
    else:
        selected_category = None

    # Si un produit spécifique est sélectionné dans la liste alphabétique
    if product_id:
        products_qs = products_qs.filter(id=product_id)

    if query:
        products_qs = products_qs.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if gender_filter in ('women', 'men', 'unisex'):
        products_qs = products_qs.filter(gender=gender_filter)

    if scent_family_filter:
        products_qs = products_qs.filter(scent_family=scent_family_filter)

    if sort == 'price_asc':
        products_qs = products_qs.order_by('price')
    elif sort == 'price_desc':
        products_qs = products_qs.order_by('-price')
    elif sort == 'newest':
        products_qs = products_qs.order_by('-created_at')
    elif sort == 'bestseller':
        products_qs = products_qs.order_by('-is_bestseller', 'name')

    cart = get_cart_from_session(request)
    cart_count = sum(cart.values())

    context = {
        'categories': categories,
        'products': products_qs,
        'all_products_sidebar': all_products_sidebar,
        'selected_category': selected_category,
        'cart_count': cart_count,
        'gender_filter': gender_filter,
        'scent_family_filter': scent_family_filter,
        'sort': sort,
        'gender_choices': [('women', 'Femme'), ('men', 'Homme'), ('unisex', 'Unisexe')],
        'scent_family_choices': [
            ('floral', 'Fleuri'), ('fresh', 'Frais'), ('gourmand', 'Gourmand'),
            ('herbal', 'Herbacé'), ('earthy', 'Terreux'), ('warm', 'Chaud'),
        ],
    }
    return render(request, 'products.html', context)


def product_detail(request, slug):
    """Fiche produit détaillée : galerie, notes olfactives, inspiration luxe, avis, produits associés"""
    product = get_object_or_404(Product, slug=slug, is_available=True)

    # Traitement du formulaire d'avis
    if request.method == 'POST' and 'submit_review' in request.POST:
        author = request.POST.get('author', '').strip()
        rating = request.POST.get('rating')
        text = request.POST.get('text', '').strip()
        if author and rating and text:
            Review.objects.create(product=product, author=author, rating=int(rating), text=text)
            messages.success(request, "Merci ! Votre avis a été ajouté avec succès. 💎")
            return redirect('shop:product_detail', slug=product.slug)

    related_products = (
        Product.objects.filter(is_available=True)
        .filter(Q(category=product.category) | Q(scent_family=product.scent_family))
        .exclude(id=product.id)
        .distinct()[:4]
    )

    cart = get_cart_from_session(request)
    cart_count = sum(cart.values())

    context = {
        'product': product,
        'related_products': related_products,
        'categories': Category.objects.all(),
        'cart_count': cart_count,
    }
    return render(request, 'product_detail.html', context)


@require_POST
def add_to_cart(request):
    """Ajoute un produit au panier"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_available=True)
        
        cart = get_cart_from_session(request)
        
        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity
        
        save_cart_to_session(request, cart)
        cart_count = sum(cart.values())
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} ajouté au panier',
            'cart_count': cart_count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@require_POST
def update_cart(request):
    """Met à jour la quantité d'un produit au panier"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 0))
        
        cart = get_cart_from_session(request)
        
        if quantity <= 0:
            if product_id in cart:
                del cart[product_id]
        else:
            cart[product_id] = quantity
        
        save_cart_to_session(request, cart)
        
        total = calculate_cart_total(cart)
        cart_count = sum(cart.values())
        
        return JsonResponse({
            'success': True,
            'total': float(total),
            'cart_count': cart_count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@require_POST
def remove_from_cart(request):
    """Supprime un produit du panier"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        
        cart = get_cart_from_session(request)
        
        if product_id in cart:
            del cart[product_id]
        
        save_cart_to_session(request, cart)
        
        total = calculate_cart_total(cart)
        cart_count = sum(cart.values())
        
        return JsonResponse({
            'success': True,
            'total': float(total),
            'cart_count': cart_count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


def view_cart(request):
    """Affiche le panier détaillé"""
    cart = get_cart_from_session(request)
    
    cart_items = []
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': product.price * quantity
            })
        except Product.DoesNotExist:
            continue
    
    subtotal = calculate_cart_total(cart)
    cart_count = sum(cart.values())
    discount_percent = get_quantity_discount(cart_count)
    discount_amount = (subtotal * discount_percent / 100) if discount_percent else Decimal('0.00')
    total = subtotal - discount_amount
    categories = Category.objects.all()

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_percent': discount_percent,
        'discount_amount': discount_amount,
        'total': total,
        'categories': categories,
        'cart_count': cart_count,
        'discount_rules': QuantityDiscountRule.objects.filter(is_active=True).order_by('min_quantity'),
    }
    return render(request, 'cart.html', context)


def checkout(request):
    """Page de paiement et commande"""
    cart = get_cart_from_session(request)
    
    if not cart:
        return redirect('shop:view_cart')
    
    cart_items = []
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': product.price * quantity
            })
        except Product.DoesNotExist:
            continue
    
    subtotal = calculate_cart_total(cart)
    cart_item_count = sum(cart.values())
    discount_percent = get_quantity_discount(cart_item_count)
    discount_amount = (subtotal * discount_percent / 100) if discount_percent else Decimal('0.00')
    total = subtotal - discount_amount
    categories = Category.objects.all()
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        delivery_date = request.POST.get('delivery_date', 'today')
        
        # Validation basique
        errors = []
        if not full_name:
            errors.append('Le nom complet est requis')
        if not phone:
            errors.append('Le numéro WhatsApp est requis')
        if not address:
            errors.append('L\'adresse de livraison est requise')
        
        if errors:
            context = {
                'cart_items': cart_items,
                'subtotal': subtotal,
                'discount_percent': discount_percent,
                'discount_amount': discount_amount,
                'total': total,
                'categories': categories,
                'errors': errors,
                'form_data': request.POST,
                'cart_count': sum(cart.values()),
                'discount_rules': QuantityDiscountRule.objects.filter(is_active=True).order_by('min_quantity'),
            }
            return render(request, 'checkout.html', context)
        
        # Créer la commande
        order = Order.objects.create(
            full_name=full_name,
            phone=phone,
            address=address,
            delivery_date=delivery_date,
            subtotal_price=subtotal,
            discount_percent=discount_percent,
            total_price=total
        )
        
        # Créer les items de la commande
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=int(product_id))
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
            except Product.DoesNotExist:
                continue
        
        # Vider le panier
        request.session['cart'] = {}
        request.session.modified = True
        
        # Générer le message WhatsApp
        message = order.get_whatsapp_message()
        # Envoyer vers le numéro ADMIN, pas l'utilisateur
        admin_phone = settings.WHATSAPP_ADMIN_PHONE.lstrip('+')
        whatsapp_url = f"https://wa.me/{admin_phone}?text={urllib.parse.quote(message)}"
        
        return render(request, 'order_confirmation.html', {
            'order': order,
            'whatsapp_url': whatsapp_url,
            'message': message,
            'categories': categories,
            'WHATSAPP_ADMIN_PHONE': settings.WHATSAPP_ADMIN_PHONE,
        })
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_percent': discount_percent,
        'discount_amount': discount_amount,
        'total': total,
        'categories': categories,
        'cart_count': sum(cart.values()),
        'discount_rules': QuantityDiscountRule.objects.filter(is_active=True).order_by('min_quantity'),
    }
    return render(request, 'checkout.html', context)


@require_POST
def newsletter_subscribe(request):
    """Inscription à la newsletter depuis le footer (section 'Soyez la première informée')"""
    email = request.POST.get('email', '').strip()
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'

    if not email or '@' not in email:
        messages.error(request, "Merci de renseigner une adresse email valide.")
        return redirect(next_url)

    existing = NewsletterSubscriber.objects.filter(email__iexact=email).first()
    if existing:
        messages.info(request, "Cette adresse est déjà inscrite à notre newsletter.")
    else:
        NewsletterSubscriber.objects.create(email=email)
        messages.success(request, "Merci ! Vous êtes bien inscrit(e) à notre newsletter. 💎")
    return redirect(next_url)
