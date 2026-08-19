# Guide de déploiement — Mise à jour KATAUPARFUM

## ⚠️ Avant tout : sauvegarde de la base Supabase
1. Dans le dashboard Supabase → Database → Backups (ou via `pg_dump` si tu as l'URL de connexion).
2. Fais un export complet avant de continuer. Si quelque chose se passe mal, tu pourras restaurer.

## 1. Installer les nouvelles dépendances (rien de nouveau normalement, le projet utilise les mêmes librairies)
```bash
pip install -r requirements.txt --break-system-packages
```

## 2. Appliquer les migrations
```bash
python manage.py migrate
```
Ceci va, dans l'ordre :
- Ajouter tous les nouveaux champs produits (genre, notes, famille olfactive, etc.) — vides par défaut, aucune donnée existante n'est perdue
- Générer automatiquement un slug unique pour chaque produit déjà en base (ex: "Essence Précieuse" → `essence-precieuse`)
- Créer les tables `ProductImage`, `QuantityDiscountRule`, `SiteSettings`

## 3. Collecter les fichiers statiques (si déploiement via Render/Railway)
```bash
python manage.py collectstatic --noinput
```

## 4. Vérifier dans l'admin Django (`/admin/`)
- **Produits** : remplir progressivement les nouveaux champs (genre, notes, famille olfactive, "inspiré de"...) pour chaque produit. Rien n'est obligatoire, le site fonctionne même si ces champs restent vides.
- **Réglages du site** : uploader la vidéo hero (MP4, quelques secondes, légère) ou coller un lien vidéo externe. Si aucune vidéo n'est ajoutée, l'image de fond actuelle reste utilisée automatiquement.
- **Règles de réduction par quantité** : optionnel. Exemple : 3 articles = -10%, 4 = -15%, 5 = -20%. Ta cliente peut désactiver une règle à tout moment (case "is_active") sans la supprimer.

## 5. Déployer
Pousse le code sur ta branche de déploiement habituelle (Render déploiera automatiquement si c'est configuré ainsi). Prévois de le faire à un moment calme (peu de commandes en cours), le site sera brièvement indisponible pendant le redéploiement — comme à chaque mise à jour normale.

## 6. Vérification post-déploiement
- [ ] La page d'accueil s'affiche
- [ ] La fiche produit d'un article s'ouvre (`/produit/<slug>/`)
- [ ] Le panier fonctionne, l'ajout au panier fonctionne
- [ ] Une commande test peut être passée jusqu'au bout
- [ ] L'admin est accessible et les nouveaux champs sont visibles

## Nouveautés livrées dans cette mise à jour
- Modèle produit enrichi : genre, notes olfactives (tête/cœur/fond), famille olfactive, intensité, concentration, contenance, "inspiré de" + économie affichée, badges Bestseller/Nouveau, prix barré
- Galerie multi-images par produit
- Nouvelle fiche produit détaillée (`/produit/<slug>/`)
- Filtres genre + famille olfactive + tri sur la page produits (desktop et mobile)
- Réduction automatique par quantité, 100% optionnelle et pilotable depuis l'admin
- Page d'accueil : vidéo hero en boucle (optionnelle), bandeau de réassurance, blocs "Shop by Gender", carrousel horizontal de produits vedettes avec flèches
- Système de prix unifié partout (même police pour le chiffre et "FCFA", plus aucune incohérence entre les pages)
