from django.urls import path
from .views import (
    HomeView,
    ItemDetailView,
    checkout
)


app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='homepage'),
    path('detail/<slug>/', ItemDetailView.as_view(), name='item-detail'),
    path('checkout/', checkout, name='item-checkout'),
]
