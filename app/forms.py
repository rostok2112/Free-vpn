from django import forms
from .models import Site


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
        url = self.cleaned_data['url']
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
