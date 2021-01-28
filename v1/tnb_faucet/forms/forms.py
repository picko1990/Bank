from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible
from django import forms

from ..models.tnb_faucet import FaucetOption


class FaucetForm(forms.Form):
    # captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)
    url = forms.URLField(required=True,
                         widget=forms.TextInput
                         (attrs={
                             'placeholder': ('URL of a facebook post'
                                             ' or tweet containing your thenewboston'
                                             ' address...')})
                         )
    amount = forms.ModelChoiceField(
        queryset=FaucetOption.objects.all(),
        initial=FaucetOption.objects.first()
    )
