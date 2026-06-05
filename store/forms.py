from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import CustomerProfile, Address


def clean_contact_number_value(contact_number):
    cleaned = contact_number.strip()
    if not cleaned:
        return cleaned
    digits = cleaned.replace(" ", "").replace("-", "")
    if not digits.isdigit() or len(digits) < 10:
        raise forms.ValidationError("Enter a valid contact number.")
    return cleaned


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label="Full name", max_length=120)

    class Meta:
        model = User
        fields = ["first_name", "email", "username", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.email = self.cleaned_data["email"].lower()
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(label="Full name", max_length=120)
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomerProfile
        fields = ["full_name", "email", "photo", "photo_url", "contact_number", "address", "city", "state", "pincode"]
        labels = {
            "photo": "Upload profile photo",
            "photo_url": "Profile photo URL",
            "contact_number": "Contact number",
            "address": "Delivery address",
            "pincode": "PIN code",
        }
        widgets = {
            "photo": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "photo_url": forms.URLInput(attrs={"placeholder": "https://example.com/my-photo.jpg"}),
            "address": forms.Textarea(attrs={"rows": 4, "placeholder": "House no, street, area"}),
            "contact_number": forms.TextInput(attrs={"placeholder": "10-digit mobile number"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "state": forms.TextInput(attrs={"placeholder": "State"}),
            "pincode": forms.TextInput(attrs={"placeholder": "PIN code"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["full_name"].initial = self.user.first_name
        self.fields["email"].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.exclude(id=self.user.id).filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_contact_number(self):
        return clean_contact_number_value(self.cleaned_data["contact_number"])

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.first_name = self.cleaned_data["full_name"]
        self.user.email = self.cleaned_data["email"]
        if commit:
            self.user.save()
            profile.save()
        return profile


class CheckoutForm(forms.Form):
    contact_number = forms.CharField(
        label="Contact number",
        max_length=15,
        widget=forms.TextInput(attrs={"placeholder": "10-digit mobile number"}),
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "House no, street, city, pincode"}),
        label="Delivery address",
    )
    payment_method = forms.ChoiceField(
        label="Payment mode",
        choices=[
            ("Demo payment", "Demo payment"),
            ("Cash on delivery", "Cash on delivery"),
            ("UPI demo", "UPI demo"),
            ("Card demo", "Card demo"),
        ],
    )
    payment_amount = forms.DecimalField(
        label="Payment amount",
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01", "placeholder": "Enter order total"}),
    )

    def clean_contact_number(self):
        return clean_contact_number_value(self.cleaned_data["contact_number"])


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'line1', 'line2', 'city', 'state', 'pincode', 'is_default']
        labels = {
            'full_name': 'Full name',
            'line1': 'Address line 1',
            'line2': 'Address line 2 (optional)',
            'city': 'City',
            'state': 'State',
            'pincode': 'PIN code',
            'is_default': 'Set as default address',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Enter full name'}),
            'line1': forms.TextInput(attrs={'placeholder': 'House no, street, area'}),
            'line2': forms.TextInput(attrs={'placeholder': 'Landmark, apartment (optional)'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State'}),
            'pincode': forms.TextInput(attrs={'placeholder': '6-digit PIN code'}),
        }