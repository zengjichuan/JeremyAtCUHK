__author__ = 'admin'
from django import forms
from django.utils.translation import ugettext_lazy as _

SCHOOL_CHOICES = (
    ('CUHK', _('Chinese University of Hong Kong')),
    ('CityU', _('City University of Hong Kong')),
    ('HKBU', _('Hong Kong Baptist University')),
    ('HKU', _('Hong Kong University')),
    ('PolyU', _('Hong Kong Polytechnic University')),
    ('HKUST', _('Hong Kong University of Science and Technology')),
    ('LNU', _('Lingnan University')),
    ('OUHK', _('Open University of Hong Kong')),
    ('OtherU', _('Other tertiary institution of Hong Kong')),
    ('Other', _('Others')),
)

CHRISTIAN_CHOICES = (
    ('No', 'No'),
    ('Yse', 'Yes'),
)
class UserForm(forms.Form):
    name = forms.CharField(max_length=30)
    email = forms.EmailField()
    school = forms.ChoiceField(choices=SCHOOL_CHOICES)
    # chris = forms.ChoiceField(choices=CHRISTIAN_CHOICES, widget=forms.RadioSelect, required=False)
    # invite = forms.CharField(widget=forms.Textarea, required=False, max_length=512)

class InviteForm(forms.Form):
    invite = forms.CharField(widget=forms.Textarea, required=False, max_length=512)