from django import forms



class AdminLoginForm(forms.Form):
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