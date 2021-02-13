# file mygame/web/chargen.views.py

from django.shortcuts import render

# Create your views here.

from web.chargen.models import CharApp
from django.http import HttpResponseRedirect
from datetime import datetime
from evennia.objects.models import ObjectDB
from django.conf import settings
from evennia.utils import create

def index(request):
    current_user = request.user # current user logged in
    p_id = current_user.id # the account id
    # submitted Characters by this account
    sub_apps = CharApp.objects.filter(account_id=p_id, submitted=True)
    context = {'sub_apps': sub_apps}
    # make the variables in 'context' available to the web page template
    return render(request, 'chargen/index.html', context)

def detail(request, app_id):
    app = CharApp.objects.get(app_id=app_id)
    sexus = app.sexus
    gens = app.gens
    praenomen = app.praenomen
    p_id = request.user.id
    context = {
            'sexus': sexus,
            'gens': gens,
            'praenomen': praenomen,
            'p_id': p_id,
            'submitted': submitted,
            }
    return render(request, 'chargen/detail.html', context)
