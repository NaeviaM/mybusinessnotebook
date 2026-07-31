# Rapport de santé — 2026-07-31

VERIF LIVE : IMPOSSIBLE (reseau sortant bloque)

**STATUT GLOBAL : OK**

## ACTION REQUISE UTILISATEUR

Aucune action requise aujourd'hui.

- **Vérification live impossible depuis cet environnement.** `curl` → échec de connexion (exit 56) sur `https://mybusinessnotebook.com/` et sur `https://le-carnet-du-commercant.vercel.app/`. Le statut du proxy sortant confirme : `gateway answered 403 to CONNECT (policy denial or upstream failure)` sur `mybusinessnotebook.com:443`. Ce n'est pas un défaut du site, c'est une restriction de cet environnement d'exécution — les sections A (disponibilité live) et B (balayage live du sitemap, 92 URLs) n'ont pas pu être exécutées aujourd'hui.
- **DNS : aucun problème.** Résolution via `python3 socket.getaddrinfo` (ne passe pas par le proxy HTTPS bloqué) :
  - `mybusinessnotebook.com` → `216.198.79.1` (plage Vercel)
  - `www.mybusinessnotebook.com` → `66.33.60.35` / `76.76.21.123` (plages Vercel)
  - Pas d'IP de parking Namecheap, pas de nameserver `failed-whois-verification`. DNS correctement pointé vers Vercel.

## CRITIQUE

Aucun problème critique. Sections C, D, E, F (toutes sur disque) exécutées intégralement et ressorties propres. Sections A et B non exécutées (réseau bloqué, voir ci-dessus) — ne pas interpréter cette absence comme une confirmation que le site répond en ligne.

## MOYEN

Aucun problème trouvé :
- **Intégrité des liens internes (disque)** : 93 fichiers `.html` passés en revue (hors `/sw/`, dont 92 pages de contenu + 1 fichier de vérification Google `google5f267a48e7657a47.html`), tous les `href`, `src` d'image et `background-image: url(...)` internes vérifiés (liens root-relatifs, relatifs et absolus sur le domaine, y compris JSON-LD et hreflang) — 0 lien cassé, 0 image manquante.
- **Piège des URLs sans extension** : 0 URL absolue interne (href/canonical/og:url/hreflang/JSON-LD) vers un article sans `.html`.
- **Cohérence sitemap.xml** : 92 entrées `<loc>`, correspondance exacte 1:1 avec les 92 pages de contenu sur disque (4 pages d'accueil FR/EN/ES/PT + 88 articles). 0 doublon, 0 entrée pointant vers un fichier manquant, 0 page présente sur disque et absente du sitemap.
- **Balises d'en-tête** : les 92 pages de contenu ont toutes un `title`, une `meta description`, un `canonical`, une `meta robots`, un `og:image`, un `viewport`, et exactement un seul `h1`. 0 page en défaut. 0 `canonical`/`og:url` utilisant `www`. (Le fichier `google5f267a48e7657a47.html` n'a volontairement aucune de ces balises : c'est un simple fichier de vérification Google Search Console, pas une page — comportement normal, non compté comme défaut.)

Répartition par langue (hors `/sw/`) : FR 26 pages (accueil + 25 articles), EN 24 (accueil + 23 articles), ES 19 (accueil + 18 articles), PT 23 (accueil + 22 articles) — total 92 pages de contenu + 1 fichier de vérification Google.

## COSMETIQUE

Aucun problème trouvé :
- 0 carte `pc-ph` (tuile emoji/dégradé) sur les 4 pages d'accueil — toutes les cartes utilisent `pc-media` avec une vraie photo en `background-image` (FR 22, EN 22, ES 16, PT 20 cartes).
- 0 article sans section `related-block` sur les 88 articles contrôlés.

## CORRIGE AUTOMATIQUEMENT

Aucune correction nécessaire aujourd'hui : toutes les vérifications sur disque (C, D, E, F) sont ressorties propres. Aucun fichier de contenu, sitemap ou tête de page n'a été modifié.
