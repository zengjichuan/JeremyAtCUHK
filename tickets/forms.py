__author__ = 'admin'
from django import forms

SCHOOL_CHOICES = (
    ('CUHK', 'Chinese University of Hong Kong'),
    ('CityU', 'City University of Hong Kong'),
    ('HKBU', 'Hong Kong Baptist University'),
    ('HKU', 'Hong Kong University'),
    ('PolyU', 'Hong Kong Polytechnic University'),
    ('HKUST', 'Hong Kong University of Science and Technology'),
    ('LNU', 'Lingnan University'),
    ('OUHK', 'Open University of Hong Kong'),
    ('Other', 'Other'),
)

CHRISTIAN_CHOICES = (
    ('No', 'No'),
    ('Yse', 'Yes'),
)
class UserForm(forms.Form):
    name = forms.CharField(max_length=30)
    email = forms.EmailField()
    school = forms.ChoiceField(choices=SCHOOL_CHOICES)
    chris = forms.ChoiceField(choices=CHRISTIAN_CHOICES, widget=forms.RadioSelect, required=False)
    invite = forms.CharField(widget=forms.Textarea, required=False)
