from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

class CustomLoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You are not logged in!')
            return redirect(reverse_lazy('login'))
        return super().dispatch(request, *args, **kwargs)
    