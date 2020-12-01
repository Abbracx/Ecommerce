from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import reverse
from django.utils.text import slugify
import random, string, uuid
from django_countries.fields import CountryField

# Create your models here.


CATEGORY_CHOICES = (
    ('S','Shirt'),
    ('SW','Sport wear'),
    ('OW','Outwear'),
)

LABEL_CHOICES = (
    ('P','primary'),
    ('S','secondary'),
    ('D','danger'),
)


def _random_string_generator( size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(null=True, blank=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:item-detail', kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse('core:add-to-cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('core:remove-from-cart', kwargs={'slug': self.slug})

    def unique_slug_generator(self, new_slug=None):

        if new_slug is not None:
            slug = new_slug
        else:
            slug = slugify(self.title)

        Klass = self.__class__
        qs_exists = Klass.objects.filter(slug=slug).exists()
        if qs_exists:
            new_slug = f'{slug}-{_random_string_generator(4)}'
            return self.unique_slug_generator(new_slug=new_slug)
        return slug


    def save(self, *args, **kwargs):
        self.slug = self.unique_slug_generator()
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.quantity} of {self.item.title}'

    def get_total_quantity_price(self):
        return f'{self.quantity * self.item.price}'

    def get_total_quantity_item_discount_price(self):
        return f'{self.quantity * self.item.discount_price}'

    def get_amount_saved(self):
        return float(self.get_total_quantity_price()) - float(self.get_total_quantity_item_discount_price())

    def get_final_price(self):
        if self.item.discount_price:
            return float(self.get_total_quantity_item_discount_price())
        return float(self.get_total_quantity_price())

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} orders'

    def get_total(self):
        total = 0.0
        for order_item in self.items.all():
            final_price = order_item.get_final_price()
            total += final_price
        return total

class BillingAddress(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    appartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    # same_billing_address
    # save_info
    # payment_option

    def __str__(self):
        return f'{self.user.username} billings.'
