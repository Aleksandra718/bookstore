from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.template.response import TemplateResponse
from django.contrib import messages
from django.db import transaction
from main.models import Product
from .models import Cart, CartItem
from .forms import AddToCartForm, UpdateCartItemForm
import json


class CartMixin:
    def get_cart(self, request):
        if hasattr(request, 'cart'):
            return request.cart
        
        if not request.session.session_key:
            request.session.create()

        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key
        )

        request.session['cart_id'] = cart.id
        request.session.modified = True
        return cart 
    

class CartModalView(CartMixin, View):
    def get_cart(self, request):
        cart = self.get_cart(request)
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related(
                'product',  
            ).order_by('-added_at')
        }
        return TemplateResponse(request, 'cart/cart_modal.html', context)


class AddToCartView(CartMixin, View):
    @transaction.atomic
    def post(self, request, slug):
        cart = self.get_cart(request)
        product = get_object_or_404(Product, slug=slug)

        form = AddToCartForm(request.POST, product=product)

        if not form.is_valid():
            return JsonResponse({
                'error': 'Invalid form data',
                'errors': form.errors,
            }, status=400)
        
        existing_item = cart.item.filter(
            product=product,
        ).first()

        cart_item = cart.add_product(product, quantity)

        request.session['cart_id'] = cart.id
        request.session.modified = True

        if request.headers.get('HX-Request'):
            return redirect('cart:cart_modal')
        else:
            return JsonResponse({
                'succes': True,
                'total_items': cart.total_items,
                'message': f"{product.name} added to cart",
                'cart_item_id': cart_item.id
            })
        

class UpdateCartItemView(CartMixin, View):
    @transaction.atomic
    def post(self, request, item_id):
        cart = self.get_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        quantity = int(request.POST.get('quantity'), 1)

        if quantity < 0:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)
        
        if quantity == 0:
            cart_item.delete()

            cart_item.quantity = quantity
            cart_item.save()

        request.session['cart_id'] = cart.id
        request.session.modified = True

        context = {
            'cart': cart,
            'cart_items': cart.items.select_related(
                'product',  
            ).order_by('-added_at')
        }
        return TemplateResponse(request, 'cart/cart_modal.html', context)
    

class RemoveCartItemView(CartMixin, View):
    def post(self, request, item_id):
        cart = self.get_cart(request)

        try:
            cart_item = cart.items.get(id=item_id)
            cart_item.delete()

            request.session['cart_id'] = cart.id
            request.session.modified = True

            context = {
                'cart': cart,
                'cart_items': cart.items.select_related(
                    'product',  
                ).order_by('-added_at')
            }
            return TemplateResponse(request, 'cart/cart_modal.html', context)
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=400)
        

class CountView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)

        return JsonResponse({
            'total_items': cart.total_items,
            'subtotal': float(cart.subtotal)
        })
    

class ClearCartView(CartMixin, View):
     def post(self, request, item_id):
        cart = self.get_cart(request)
        cart.clear()

        request.session['cart_id'] = cart.id
        request.session.modified = True

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'cart/cart_empty.html', {
                'cart': cart
            })
        return JsonResponse({
            'succes': True,
            'message': 'Cart cleared'
        })
     
     
class CartSummaryView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        context = {
                'cart': cart,
                'cart_items': cart.items.select_related(
                    'product',  
                ).order_by('-added_at')
            }
        return TemplateResponse(request, 'cart/cart_summary.html', context)



