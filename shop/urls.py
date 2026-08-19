from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('produit/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # API endpoints
    path('api/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('api/update-cart/', views.update_cart, name='update_cart'),
    path('api/remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
]
