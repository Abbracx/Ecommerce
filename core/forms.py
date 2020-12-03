from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S','Stripe'),
    ('P', 'PayPal'),
    ('PS', 'PayStack'),
    )
class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Jos city, Plateau State...', 'class':'form-control'
        }))
    appartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder':'House no.5b Rayfield, Opposite Govt House...', 'class':'form-control'
        }))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100 form-control', 'placeholder':'(choose your country)'
        }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control'
        }))
    same_billing_address = forms.BooleanField(widget=forms.CheckboxInput(), required="False")
    save_info = forms.BooleanField(widget=forms.CheckboxInput(), required="False")
    payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)

