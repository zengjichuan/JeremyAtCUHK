__author__ = 'admin'
from django import forms
from django.utils.translation import ugettext_lazy as _

SCHOOL_CHOICES = (
    ('CityU', _('City University of Hong Kong')),
    ('HKBU', _('Hong Kong Baptist University')),
    ('LNU', _('Lingnan University')),
    ('CUHK', _('Chinese University of Hong Kong')),
    ('HKIEd', _('The Hong Kong Institute of Education')),
    ('PolyU', _('Hong Kong Polytechnic University')),
    ('HKUST', _('Hong Kong University of Science and Technology')),
    ('HKU', _('Hong Kong University')),
    # ('OUHK', _('Open University of Hong Kong')),
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