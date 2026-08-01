# Rapport de santé — 2026-08-01

VERIF LIVE : IMPOSSIBLE (reseau sortant bloque)

**STATUT GLOBAL : OK**

## ACTION REQUISE UTILISATEUR

Aucune action requise aujourd'hui.

- **Vérification live impossible depuis cet environnement.** `curl` → `CONNECT tunnel failed, response 403` sur `https://mybusinessnotebook.com/`. Le statut du proxy sortant confirme : `gateway answered 403 to CONNECT (policy denial or upstream failure)` sur `mybusinessnotebook.com:443`. `WebFetch` a également renvoyé un 403. Ce n'est pas un défaut du site, c'est une restriction de cet environnement d'exécution — les sections A (disponibilité live) et B (balayage live du sitemap, 93 URLs) n'ont pas pu être exécutées aujourd'hui.
- **DNS : aucun problème.** Résolution via `python3 socket.getaddrinfo` (ne passe pas par le proxy HTTPS bloqué) :
  - `mybusinessnotebook.com` → `216.198.79.1` (plage Vercel)
  - `www.mybusinessnotebook.com` → `66.33.60.66` / `76.76.21.142` (plages Vercel)
  - Pas d'IP de parking Namecheap, pas de nameserver `failed-whois-verification`. DNS correctement pointé vers Vercel.

## CRITIQUE

Aucun problème critique. Sections C, D, E, F (toutes sur disque) exécutées intégralement et ressorties propres. Sections A et B non exécutées (réseau bloqué, voir ci-dessus) — ne pas interpréter cette absence comme une confirmation que le site répond en ligne.

## MOYEN

Aucun problème trouvé :
- **Intégrité des liens internes (disque)** : 94 fichiers `.html` passés en revue (hors `/sw/`, dont 93 pages de contenu + 1 fichier de vérification Google `google5f267a48e7657a47.html`), tous les `href`, `src` d'image, `background-image: url(...)`, liens JSON-LD (`url`/`@id`/`item` des breadcrumbs) et balises `hreflang` internes vérifiés — 0 lien cassé, 0 image manquante. (9 liens `?lang=xx` détectés initialement comme suspects par le script se sont révélés corrects après vérification de `middleware.js` : le sélecteur de langue redirige côté serveur vers l'accueil de la langue choisie quelle que soit la page source, comportement normal et voulu.)
- **Piège des URLs sans extension** : 0 URL absolue interne (href/canonical/og:url/hreflang/JSON-LD/breadcrumb) vers un article sans `.html`.
- **Cohérence sitemap.xml** : 93 entrées `<loc>`, correspondance exacte 1:1 avec les 93 pages de contenu sur disque (4 pages d'accueil FR/EN/ES/PT + 89 articles). 0 doublon, 0 entrée pointant vers un fichier manquant, 0 page présente sur disque et absente du sitemap.
- **Balises d'en-tête** : les 93 pages de contenu ont toutes un `title`, une `meta description`, un `canonical`, une `meta robots`, un `og:image`, un `viewport`, et exactement un seul `h1`. 0 page en défaut. 0 `canonical`/`og:url` utilisant `www`. (Le fichier `google5f267a48e7657a47.html` n'a volontairement aucune de ces balises : simple fichier de vérification Google Search Console, comportement normal, non compté comme défaut.)

Répartition par langue (hors `/sw/`) : FR 26 pages (accueil + 25 articles), EN 25 (accueil + 24 articles), ES 19 (accueil + 18 articles), PT 23 (accueil + 22 articles) — total 93 pages de contenu + 1 fichier de vérification Google.

## COSMETIQUE

Aucun problème trouvé :
- 0 carte `pc-ph` (tuile emoji/dégradé) sur les 4 pages d'accueil — toutes les cartes utilisent `pc-media` avec une vraie photo en `background-image` (FR 22, EN 23, ES 16, PT 20 cartes).
- 0 article sans section `related-block` sur les 89 articles contrôlés.

## CORRIGE AUTOMATIQUEMENT

Aucune correction nécessaire aujourd'hui : toutes les vérifications sur disque (C, D, E, F) sont ressorties propres. Aucun fichier de contenu, sitemap ou tête de page n'a été modifié.
