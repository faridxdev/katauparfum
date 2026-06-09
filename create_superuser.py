import os
import django

# Configuration de l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "katauparfum.settings")
django.setup()

from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    
    # Récupérer les infos depuis les variables d'environnement Render
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if not all([username, email, password]):
        print("⚠️ Variables d'environnement manquantes (DJANGO_SUPERUSER_USERNAME, EMAIL, PASSWORD).")
        print("ℹ️ Le superutilisateur ne sera pas créé automatiquement.")
        return

    if not User.objects.filter(username=username).exists():
        print(f"Création du superutilisateur '{username}'...")
        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            print("✅ Superutilisateur créé avec succès !")
        except Exception as e:
            print(f"❌ Erreur lors de la création : {e}")
    else:
        print(f"ℹ️ Le superutilisateur '{username}' existe déjà.")

if __name__ == "__main__":
    create_superuser()
