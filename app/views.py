from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect,render
from django.urls import reverse
from django.contrib.auth import authenticate, login,logout
from .forms import *
from .models import *
from django.db.models import Q
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode



# Create your views here.

def inscription(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            cni = form.cleaned_data.get('cni')
            email = form.cleaned_data.get('email')

            # Vérification de l'existence de l'utilisateur avec le même CNI ou e-mail
            if Profile.objects.filter(Q(cni=cni) | Q(email=email)).exists():
                messages.error(request, 'Un utilisateur avec le même CNI ou e-mail existe déjà')
                return redirect('inscription')

            # Création de l'utilisateur et du profil
            user = form.save()
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # Authentification et connexion de l'utilisateur
            user = authenticate(request, username=username, password=password)
            login(request, user)

            # Redirection vers la page d'accueil
            return redirect('accueil')
    else:
        form = ProfileForm()
    return render(request, 'inscription.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                #bach irj3 ikml dakchi li kan taydir après l'inscription
                next_url = request.GET.get('next')
                if next_url:
                   return redirect(next_url)
                if request.user.is_staff:
                   return redirect('/admin')
                else:
                   return redirect('accueil')
    else:
        form = LoginForm()
    return render(request, 'user_login.html', {'form': form})

def deconnexion(request):
    logout(request)
    return redirect('accueil')


def accueil(request):
    if request.user.is_authenticated and request.user.is_staff:
        logout(request)
        return redirect('accueil')
    livres = Livre.objects.filter(disponible=True)
    return render(request, 'accueil.html', {'livres': livres})

# def test(request):
#     return render(request,'test.html')


def chercher_livre(request):
    if request.method == 'GET':
        search_bar = request.GET.get('search_bar')
        search_choice = request.GET.get('search_choice')
        if search_bar and search_choice:
            if search_choice == 'titre':
                livres = Livre.objects.filter(titre__icontains=search_bar,disponible=True)
            elif search_choice == 'auteur':
                livres = Livre.objects.filter(auteur__nom__icontains=search_bar,disponible=True)
            elif search_choice == 'domaine':
                livres = Livre.objects.filter(domaine__nom__icontains=search_bar,disponible=True)
            else:
                livres = Livre.objects.none()
        else:
            livres = Livre.objects.none()
    else:
        livres = Livre.objects.none()
    # Stocker les valeurs précédentes dans la session
    request.session['search_bar'] = request.GET.get('search_bar', '')
    request.session['search_choice'] = request.GET.get('search_choice', '')


    context = {'livres': livres}
    return render(request, 'accueil.html', context)

@login_required(login_url='user_login')  # Décorateur pour vérifier l'authentification de l'utilisateur
def supprimer_emprunt(request, emprunt_id):
    emprunt = Emprunt.objects.get(id=emprunt_id)
    if not emprunt.est_rendu:
        # Mettre à jour la disponibilité du livre associé
        livre = emprunt.livre.first()
        if livre:
            livre.disponible = True
            livre.save()
        emprunt.delete()
        messages.success(request, "L'emprunt a été supprimé avec succès.")

    else:
        messages.error(request, "Impossible de supprimer un emprunt déjà rendu.")
        
    return redirect('espace_personnel')


@login_required(login_url='user_login')  # Décorateur pour vérifier l'authentification de l'utilisateur
def emprunter_livre(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)

    # Mettre à jour la disponibilité du livre
    livre.disponible = False
    livre.save()

    # Ajouter l'emprunt dans le profil de l'étudiant
    # Ajouter l'emprunt dans le profil de l'étudiant
    profile = request.user.profile
    emprunt = Emprunt(profile=profile)
    emprunt.save()
    emprunt.livre.add(livre)
    
    # Ajouter un message de succès
    messages.success(request, f"Le livre: '{livre.titre}' a été emprunté avec succès.")

    # Récupérer les valeurs précédentes de la session
    search_bar = request.session.get('search_bar', '')
    search_choice = request.session.get('search_choice', '')
    if not search_bar and not search_choice:
        # Les paramètres de recherche sont vides, rediriger vers la page d'accueil
        return redirect(reverse('accueil'))
    
    # Construire l'URL de redirection avec les paramètres de recherche
    url = reverse('recherche_livre')
    params = urlencode({'search_bar': search_bar, 'search_choice': search_choice})
    if params:
        url = f"{url}?{params}"
    
    # Rediriger l'utilisateur vers la page de recherche de livre avec les autres livres non empruntés
    return redirect(url)

@login_required(login_url='user_login')
def espace_personnel(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    emprunts_en_cours = Emprunt.objects.filter(profile=profile, est_rendu=False,est_prend=False)
    emprunts_prends = Emprunt.objects.filter(profile=profile, est_prend=True)
    emprunts_rendus = Emprunt.objects.filter(profile=profile, est_rendu=True)  # Ajout de cette ligne
    
    context = {
        'profile': profile,
        'emprunts_en_cours': emprunts_en_cours,
        'emprunts_prends': emprunts_prends,
        'emprunts_rendus': emprunts_rendus,  # Ajout de cette ligne
    }
    return render(request, 'espace_personnel.html', context)


@login_required(login_url='user_login')
def changer_information(request):
    if request.method == 'POST':
        user = request.user
        profile = Profile.objects.get(user=user)

        # Récupérer les données du formulaire
        cni = request.POST['cni']
        email = request.POST['email']
        nom = request.POST['nom']
        prenom = request.POST['prenom']

        # Vérifier si les valeurs de CNI et d'email sont uniques
        if Profile.objects.exclude(user=user).filter(cni=cni).exists():
            messages.error(request, "Cette CNI est déjà utilisée par un autre utilisateur.")
            return redirect('changer_information')
        if Profile.objects.exclude(user=user).filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé par un autre utilisateur.")
            return redirect('changer_information')

        # Mettre à jour les informations du profil
        profile.cni = cni
        profile.email = email
        profile.first_name = nom
        profile.last_name = prenom
        profile.save()

        messages.success(request, "Vos informations personnelles ont été mises à jour avec succès.")
        return redirect('espace_personnel')

    else:
        user = request.user
        profile = Profile.objects.get(user=user)
        context = {
            'profile': profile
        }
        return render(request, 'espace_personnel.html', context)


# @login_required(login_url='user_login')
# def testEspace(request):
#     user = request.user
#     profile = Profile.objects.get(user=user)
#     emprunts_en_cours = Emprunt.objects.filter(profile=profile, est_rendu=False)
#     emprunts_prends = Emprunt.objects.filter(profile=profile, est_prend=False)
#     emprunts_rendus = Emprunt.objects.filter(profile=profile, est_rendu=True)  # Ajout de cette ligne
    
#     context = {
#         'profile': profile,
#         'emprunts_en_cours': emprunts_en_cours,
#         'emprunts_prends': emprunts_prends,
#         'emprunts_rendus': emprunts_rendus,  # Ajout de cette ligne
#     }
#     return render(request, 'espace_personnel.html', context)
