from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Item, Order, OrderItem
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.contrib import messages
# Create your views here.


class HomeView(ListView):
    model = Item
    paginate_by = 4
    template_name = 'home-page.html'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'



def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
        )[0]
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, f'These product has been updated.')
            return redirect('core:item-detail', slug=item.slug)

        else:
            order.items.add(order_item)
            messages.info(request, f'These product has been added to your cart.')
            return redirect('core:item-detail', slug=item.slug)

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, order_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, f'These product has been added to your cart.')

    return redirect('core:item-detail', slug=item.slug)

def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
            item=item,
            user=request.user,
            ordered=False
            )[0]
            #order_item.quantity -= 1
            #order_item.save()
            order.items.remove(order_item)
            messages.info(request, f'These product has been removed from your cart.')
            return redirect('core:item-detail', slug=item.slug)
        else:
            messages.info(request, f'These product does not exist in your cart.')
            return redirect('core:item-detail', slug=item.slug)

    messages.info(request, f'sorry you dont have and order.')
    return redirect('core:item-detail', slug=item.slug)



def checkout(request):
    pass