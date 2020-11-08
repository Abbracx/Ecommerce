from django.shortcuts import render
from django.http import HttpResponse
from .models import Item, Order, OrderItem
from django.views.generic import ListView, DetailView
# Create your views here.


class HomeView(ListView):
    model = Item
    template_name = 'home-page.html'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'



def checkout(request):

    context = {
        'items': Item.objects.all()
    }

    return render(request, 'checkout-page.html', context)

