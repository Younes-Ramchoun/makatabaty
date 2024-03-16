from django.urls import path
from . import views


#urlsconfig for this app
urlpatterns = [
    path('',views.accueil,name='accueil'),
    path('inscription/', views.inscription, name='inscription'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('espace_personnel/', views.espace_personnel, name='espace_personnel'),


    # path('test',views.test,name='test'),
    path('changer_information/', views.changer_information, name='changer_information'),
    # path('testEspace',views.testEspace,name='testEspace'),
    path('recherche/', views.chercher_livre, name='recherche_livre'),
    path('connexion/', views.user_login, name='user_login'),
    path('emprunter/<int:livre_id>/', views.emprunter_livre, name='emprunter_livre'),
    path('supprimer_emprunt/<int:emprunt_id>/', views.supprimer_emprunt, name='supprimer_emprunt'),


]