from django.contrib.sites.shortcuts import get_current_site
from . import accounts_settings


def page_title(request):
    try:
        return {'page_title': accounts_settings.PAGES_TITLE[request.path].title()}
    except:
        current_site = get_current_site(request)
        return {'page_title': current_site.name.title()}