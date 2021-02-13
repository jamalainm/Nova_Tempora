# file mygame/web/chargen.views.py

from django.shortcuts import render

# Create your views here.

from web.chargen.models import CharApp
from django.http import HttpResponseRedirect
from datetime import datetime
from evennia.objects.models import ObjectDB
from django.conf import settings
from evennia.utils import create
from web.chargen.static.name_data.gens_class_praenomina import name_data

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
    if sexus == 'mās':
        nōmen = gens[:-1] + 'us'
    else:
        nōmen = gens
    p_id = request.user.id
    submitted = app.submitted
    context = {
            'sexus': sexus,
            'gens': gens,
            'praenōmen': praenomen,
            'nōmen': nōmen,
            'p_id': p_id,
            'submitted': submitted,
            }
    return render(request, 'chargen/detail.html', context)

def creating(request):
    user = request.user

    # Go to the first page of character creation
    if request.method != 'POST':

        genders = ['mās','muliebris']

        context = {'genders': genders}

        return render(request, 'chargen/gender_select.html', context)

    # Go to the second page of character creation
    elif not request.POST.get('gens'):

        sexus = request.POST.get('sexus')
        gentes = name_data.keys()
        context = {
                'gender': gender,
                'gentes': gentes,
                }

        return render(request, 'chargen/gens_select.html', context)

    # Go to the third and final page of character creation
    elif not request.POST.get('praenomen'):

        sexus = request.POST.get('sexus')
        gens = request.POST.get('gens')
        if sexus == 'mās':
            gender = 'masculine'
        else:
            gender = 'feminine'

        praenomina = name_data[gens]['praenomina'][gender]

        context = {
                'gender': gender,
                'gens': gens,
                'praenomina': praenomina,
                }

    else:

        sexus = request.POST.get('sexus')
        gens = request.POST.get('gens')
        praenomen = request.POST.get('praenomen')
        applied_date = datetime.now()
        submitted = True
        if 'save' in request.POST:
            submitted = False
        app = CharApp(
                sexus = sexus,
                gens = gens,
                praenomen = praenomen,
                date_applied = applied_date,
                account_id = user.id,
                submitted = submitted,
                )
        app.save()

        if submitted:
            if sexus == 'mās':
                nōmen = gens[:-1] + 'us'
            else:
                nōmen = gens
            nōmina = praenomen + ' ' + nōmen
            # Create the actual character object
            typeclass = settings.BASE_CHARACTER_TYPECLASS
            home = ObjectDB.objects.get_id(settings.GUEST_HOME)
            # turn the permissionhandler to a string
            perms = str(user.permissions)
            # create the character
            char = create.create_object(
                    typeclass = typeclass,
                    key = nōmina,
                    home = home,
                    permissions=perms,
                    attributes=[
                        ('sexus', sexus),
                        ('gens', gens),
                        ('praenōmen', praenomen),
                        ('nōmen', nōmen),
                        ]
                    )
            user.db._playable_characters.append(char)
            char.locks.add(f"puppet:id({char.id}) or pid({user.id}) or perm(Developers) or pperm(Developers);delete:id({user.id}) or perm(Admin)")

        return HttpResponseRedirect('/chargen')
