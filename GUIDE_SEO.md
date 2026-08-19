# Guide SEO — KATAUPARFUM.COM

## Ce qui a été mis en place dans le code

1. **Meta tags dynamiques** par page (titre, description, Open Graph, Twitter Card) — chaque produit a désormais son propre titre/description unique optimisé (ex: "Essence Précieuse - Inspiré de Baccarat Rouge 540 | KATAUPARFUM Lomé")
2. **`sitemap.xml`** généré automatiquement (`/sitemap.xml`) — inclut toutes les fiches produit, catégories, et pages principales, mis à jour automatiquement à chaque nouveau produit ajouté
3. **`robots.txt`** (`/robots.txt`) — autorise l'indexation, bloque panier/checkout (contenu privé sans intérêt SEO), pointe vers le sitemap
4. **Données structurées JSON-LD** :
   - `Organization` sur tout le site (aide Google à afficher le nom/logo dans les résultats)
   - `Product` sur chaque fiche produit (prix, disponibilité, note moyenne — permet l'affichage d'étoiles ⭐ directement dans Google)
   - `BreadcrumbList` (fil d'ariane visible dans les résultats de recherche)
5. **Balise `<h1>` ajoutée sur la page d'accueil** (elle n'existait pas avant — c'est l'un des signaux SEO les plus importants et il manquait)
6. **`noindex`** sur panier/checkout/confirmation (évite le contenu dupliqué/privé indexé par erreur)
7. **Images en chargement différé** (`loading="lazy"`) sous la ligne de flottaison — améliore la vitesse de chargement, un critère de classement Google
8. **Ciblage géographique Togo/Lomé** dans les meta tags (`geo.region`, `geo.placename`) et dans les textes (sans survendre — juste "Lomé, Togo" mentionné naturellement)

## Ce que TOI tu dois faire (obligatoire, hors code)

### 1. Google Search Console — indispensable, gratuit
1. Va sur https://search.google.com/search-console
2. Ajoute la propriété `katauparfum.com`
3. Vérifie la propriété via l'enregistrement DNS chez Hostinger (méthode recommandée — Search Console te donne un enregistrement TXT à coller dans la zone DNS Hostinger)
4. Une fois vérifié : Sitemaps → soumets `https://katauparfum.com/sitemap.xml`
5. Demande l'indexation manuelle de tes pages principales via "Inspection de l'URL" → "Demander une indexation" (accélère le passage de Google, surtout utile juste après le lancement)

### 2. Google Business Profile — très important pour le local (Lomé)
1. Crée une fiche sur https://business.google.com pour KATAUPARFUM à Lomé
2. Ajoute photos, horaires, numéro WhatsApp, lien vers le site
3. C'est souvent CE qui fait apparaître un commerce dans "Maps" et dans les recherches type "parfumerie Lomé"

### 3. Bing Webmaster Tools (rapide à faire, souvent oublié)
https://www.bing.com/webmasters — même principe que Google Search Console, 5 minutes, capte une partie du trafic en plus.

### 4. Réseaux sociaux
Renseigne les liens Instagram/Facebook/TikTok réels dans le JSON-LD `Organization` (`sameAs`) — actuellement vide (`"sameAs": []`) car je n'ai pas les liens. Donne-les-moi ou demande-moi de te montrer où les ajouter dans `base.html`.

### 5. Contenu
- Remplis la **description de chaque produit** avec un vrai texte unique (2-3 phrases) — actuellement certains sont probablement vides, et Google pénalise le contenu dupliqué/vide
- Plus tu ajoutes de produits avec des descriptions uniques et des mots-clés naturels ("parfum femme Lomé", "inspiration Baccarat Rouge", etc.), plus le référencement se renforce avec le temps

## Ce qu'il ne faut PAS attendre
Le SEO prend du temps — généralement 4 à 12 semaines avant de voir un effet significatif sur un nom de domaine tout juste lancé, même bien configuré techniquement. Ce que j'ai fait couvre tout le **SEO technique** (ce que le code peut faire), mais le référencement dépend aussi de facteurs que le code ne contrôle pas : ancienneté du domaine, backlinks (autres sites qui pointent vers le tien), avis clients, activité régulière (nouveaux produits, mise à jour du contenu).
