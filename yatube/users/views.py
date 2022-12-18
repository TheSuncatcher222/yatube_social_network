from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm


class SignUpView(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'includes/users/signup.html'


def login_complete(request):
    template = 'includes/users/login_complete.html'
    return render(request, template)
