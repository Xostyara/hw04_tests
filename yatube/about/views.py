from django.views.generic.base import TemplateView
from django.shortcuts import render

# Create your views here.


class AboutAuthorView(TemplateView):
    template_name: str = 'about/author.html'

    def AboutAuthorView(request, template_name):

        return render(request, template_name)


class AboutTechView(TemplateView):
    template_name: str = 'about/tech.html'

    def AboutTechView(request, template_name):

        return render(request, template_name)
