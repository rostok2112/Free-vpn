from django.contrib import admin
from django.utils.safestring import mark_safe
from app.models import Site

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_select_related   = ('user', )
    list_links            = ('user', 'url', )
    search_fields         = ('id', 'name', 'user__username', )
    readonly_fields       = ('id', )
    readonly_after_add    = ('user', ) # fields that will be read only on change form
    exclude_from_add_page = ('visit_count', 'routed_data_amount', ) # fields that will be excluded from add form 
                                                                   # and readonly on change for
    
    def get_list_display(self, request):
        if not getattr(self, '_PK_NAME', None):
            self._PK_NAME = self.get_primary_key_name()
        return [
            self._PK_NAME,
            *self.generate_link_fields(),
            *self.get_other_fields()
        ]

    def get_primary_key_name(self):
        return Site._meta.pk.name

    def generate_link_fields(self):
        return [f'{link}_link' for link in self.list_links]
    
    def get_other_fields(self):
        if not getattr(self, '_PK_NAME', None):
            self._PK_NAME = self.get_primary_key_name()
        return [field.name for field in Site._meta.fields
                if field.name not in self.list_links and field.name != self._PK_NAME]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  
            return (*self.readonly_after_add, *self.exclude_from_add_page, *self.readonly_fields)
        else:  
            return self.readonly_fields

    def get_exclude(self, request, obj=None):
        if obj: 
            return ()
        else:  
            return self.exclude_from_add_page

    def user_link(self, obj):
        out = f'<a href="/admin/auth/user/{obj.user.id}/change/">{obj.user}</a>'
        return mark_safe(out)
    user_link.short_description = 'user'
    
    def url_link(self, obj):
        out = f'<a href="{obj.url}">{obj.url}</a>'
        return mark_safe(out)
    url_link.short_description = 'url'
    