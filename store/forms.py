from django import forms
from .models import AppUser



class AppUserRegistrationForm(forms.Form):

    class Meta:
        model = AppUser
        fields = ['first_name', 'last_name', 'mobile_contact', 'address', 'email', 'password1', 'password2']

    first_name = forms.CharField(
        max_length=150, 
        required=True,
        widget=
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'First name',
                    'id':'fname',
                }
            )
        )

    last_name = forms.CharField(
        max_length=150, 
        required=True,
        widget=
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Last name',
                    'id':'lname',
                }
            )
        )

    email = forms.EmailField( 
        max_length=150, 
        required=True,
        widget=
            forms.EmailInput(
                attrs={
                        'class': 'form-control',
                        'placeholder': 'Enter email address',
                        'id':'email',
                    }
                )
        )

    mobile = forms.CharField( 
        max_length=150, 
        required=True,
        widget=
            forms.TextInput(
                attrs={
                        'class': 'form-control',
                        'placeholder': 'Enter mobile number',
                        'id':'mobile-number',
                    }
                )
        )


    address = forms.CharField(
        max_length=150, 
        required=True,
        widget=
            forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter delivery address',
                    'id':'address',
                }
            )
        )


    password1 = forms.CharField( 
    label="Password",
    max_length=150, 
    required=True,
    widget=
        forms.PasswordInput(
            attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter Password',
                    'id':'password',
                }
            )
    )

    password2 = forms.CharField( 
    label="Confirm Password",
    max_length=150, 
    required=True,
    widget=
        forms.PasswordInput(
            attrs={
                    'class': 'form-control',
                    'placeholder': 'Confirm Password',
                    'id':'cpassword',
                }
            )
    )


class AppUserLoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'username or email',
            'id': 'email',
            }
        )
    )

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'password',
            }
        )
    )










