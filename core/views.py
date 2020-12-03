from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Item, Order, OrderItem, BillingAddress, Payment
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm
from django.conf import settings
# Create your views here.
import stripe
stripe.api_key = settings.STRIPE_API_KEY #"sk_test_4eC39HqLyjWDarjtT1zdp7dc"

# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token


class HomeView(ListView):
    model = Item
    paginate_by = 4
    template_name = 'home-page.html'



class OrderSummaryView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        try:
            qs = Order.objects.get(user=self.request.user, ordered=False)
            context = {'object': qs}
            return render(self.request, 'order_summary.html', context)
        except  ObjectDoesNotExist:
            messages.error(self.request, f'You do not have any order')
            return redirect('/')



class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'


@login_required
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
            return redirect('core:order-summary')

        else:
            order.items.add(order_item)
            messages.info(request, f'These product has been added to your cart.')
            return redirect('core:order-summary')

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, order_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, f'These product has been added to your cart.')

    return redirect('core:order-summary')


@login_required
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
            return redirect('core:order-summary')
        else:
            messages.info(request, f'These product does not exist in your cart.')
            return redirect('core:item-detail', slug=item.slug)

    messages.info(request, f'sorry you dont have and order.')
    return redirect('core:item-detail', slug=item.slug)


@login_required
def remove_single_item_from_cart(request, slug):
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

            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, f'These product was updated down.')
                return redirect('core:order-summary')
            else:
                order.items.remove(order_item)
                messages.info(request, f'These product was removed')
                return redirect('core:order-summary')
        else:
            messages.info(request, f'These product does not exist in your cart.')
            return redirect('core:item-detail', slug=item.slug)

    messages.info(request, f'sorry you dont have and order.')
    return redirect('core:item-detail', slug=item.slug)



class CheckOutView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        #form
        form = CheckoutForm()
        context = {
            'form': form,
            'order': order
        }
        return render(self.request, 'checkout-page.html', context)

    def post(self, *args, **kwargs):

        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address' )
                appartment_address = form.cleaned_data.get('appartment_address' )
                country = form.cleaned_data.get('country')
                zip= form.cleaned_data.get('zip')
                payment_option = form.cleaned_data.get('payment_option')
                # TODO: add functionality for shipping address
                billing_address = BillingAddress(
                    user = self.request.user,
                    street_address = street_address,
                    appartment_address = appartment_address,
                    country = country,
                    zip = zip,
                    payment_option=payment_option
                    )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

            # TODO: redirect to the payment option type

            if payment_option == "S":
                messages.success(self.request, f'details saved successfuly')
                return redirect('core:payment', payment_option=order.billing_address.get_payment_option_display())
            elif payment_option == "P":
                messages.success(self.request, f'details saved successfuly')
                return redirect('core:payment', payment_option=order.billing_address.get_payment_option_display())
            elif payment_option == "PS":
                messages.success(self.request, f'details saved successfuly')
                return redirect('core:payment', payment_option=order.billing_address.get_payment_option_display())
            else:
                messages.success(self.request, f'Invalid options selected')
                return redirect('core:item-checkout')

        except  ObjectDoesNotExist:
            messages.error(self.request, f'You do not have any order. Shop now!')
            return redirect('core:order-summary')

        messages.warning(self.request, f'form failed')
        return redirect('core:item-checkout')

class PaymentView(View):

    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)

        context = {
            "order": order
        }
        return render(self.request, 'payment.html', context)

    def post(self, *args, **kwargs):

        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:

            charge_id = stripe.Charge.create(
            amount=amount,
            currency="usd",
            source=token,
            description=f"charge for ({self.request.user.username})",
            )

            payment = Payment()
            payment.stripe_charge_id = charge_id,
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, f'Your order was successful...')
            return redirect('/')

        except stripe.error.CardError as e:
          # Since it's a decline, stripe.error.CardError will be caught
            messages.warning(self.request, f'{e.user_message}')
            return redirect('/')

        except stripe.error.RateLimitError as e:
          # Too many requests made to the API too quickly
            messages.warning(self.request, f'Rate Limit Error')
            return redirect('/')

        except stripe.error.InvalidRequestError as e:
          # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, f'Invalid Parameters')
            return redirect('/')
        except stripe.error.AuthenticationError as e:
          # Authentication with Stripe's API failed
          # (maybe you changed API keys recently)
            messages.warning(self.request, f'Not Authenticated')
            return redirect('/')
        except stripe.error.APIConnectionError as e:
          # Network communication with Stripe failed
            messages.warning(self.request, f'Network Error')
            return redirect('/')
        except stripe.error.StripeError as e:
          # Display a very generic error to the user, and maybe send
          # yourself an email
            messages.warning(self.request, f'Something went wrong. You were not charged, please try again.')
            return redirect('/')
        except Exception as e:
          # Something else happened, completely unrelated to Stripe
            messages.warning(self.request, f'Oops! serious error occured. We have bee notified.')
            return redirect('/')


