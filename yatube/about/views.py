from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'includes/about/about_author.html'


class AboutTechView(TemplateView):
    template_name = 'includes/about/about_tech.html'
