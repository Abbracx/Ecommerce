from django.shortcuts import render
from django.http import HttpResponse
from .models import Item, Order, OrderItem
# Create your views here.


def homepage(request):

    return render(request, 'home-page.html')


def item_list(request):

    context = {
        'items': Item.objects.all()
    }

    return render(request, 'Items/item_list.html', context)