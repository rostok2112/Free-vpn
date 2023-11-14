from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from app.models import Site


class BaseForm(forms.ModelForm):
    disabled_fields    = []
    add_hidden_fields  = []
    edit_hidden_fields = []
    
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name in self.disabled_fields:
            self.fields[field_name].disabled = True
            
        if not self.instance.pk: # adding new
            for field_name in self.add_hidden_fields:
                self.fields[field_name].disabled = True
        else:
            for field_name in self.edit_hidden_fields:
                self.fields[field_name].disabled = True
            
class SiteForm(BaseForm):
    disabled_fields    = ['visit_count', 'routed_data_amount',]
    add_hidden_fields  = ['visit_count', 'routed_data_amount',]

    class Meta:
        model = Site
        fields = [
            'name', 'url', 'visit_count', 'routed_data_amount',
        ]
        
    def __init__(self, *args, request=None,**kwargs):
        self.request = request
        super(SiteForm, self).__init__(*args, **kwargs)
        
        if not self.instance.pk:
            if self.request:
                self.fields['user'].initial = self.request.user
                self.fields['user'].widget = forms.HiddenInput()


    def save(self, commit=True):
        instance = super(SiteForm, self).save(commit=False)
        if not instance.user_id and self.request:
            instance.user = self.request.user

        if commit:
            instance.save()

        return instance
    
    def clean_name(self):
        name = self.cleaned_data['name']
        q = Site.objects.filter(name=name)
        if self.instance:
            q = q.exclude(id=self.instance.id)
        if q.exists():
            raise forms.ValidationError("This name is already in use. Please choose a different one.")
        return name

    def clean_url(self):
        url = self.cleaned_data['url'].lower()
        if not url.startswith(('http://', 'https://')):
            raise forms.ValidationError("Invalid URL. Please include the protocol (http:// or https://).")

        if self.instance and self.instance.id: 
            q = ( # is unique for user queryset
                Site.objects 
                    .filter(url=url)
                    .exclude(id=self.instance.id)
            )
            if getattr(self.instance, 'user', None):
                q = q.filter(user=self.instance.user)
            if q.exists():
                raise forms.ValidationError("Site url duplicate")
        return url

class CustomUserChangeForm(UserChangeForm):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput, required=False)
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password', None)
    
    def save(self, commit=True):
        user = super().save(commit=False)
        old_password = self.cleaned_data["old_password"]
        new_password = self.cleaned_data["new_password1"]

        if new_password:
            user.set_password(new_password)
        elif not new_password and old_password:
            raise forms.ValidationError("No new password provided.")
        elif not new_password and not old_password and not user.has_usable_password():
            user.password = self.initial["password"]

        if commit:
            user.save()
        return user

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if old_password and not self.instance.check_password(old_password):
            raise forms.ValidationError("Old password is incorrect.")
        return old_password

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("New passwords do not match.")
        
        validate_password(new_password2, self.instance)
        return new_password2
