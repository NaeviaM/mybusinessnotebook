# Rapport de santé — 2026-07-23

VERIF LIVE : IMPOSSIBLE (reseau sortant bloque)

**STATUT GLOBAL : OK**

## ACTION REQUISE UTILISATEUR

Aucune action requise aujourd'hui.

- **Vérification live impossible depuis cet environnement.** Le proxy sortant du bac à sable a refusé la connexion HTTPS vers `mybusinessnotebook.com` (WebFetch → `403 Forbidden` ; `curl` → `CONNECT tunnel failed, response 403` ; statut du proxy : `connect_rejected` / "gateway answered 403 to CONNECT (policy denial or upstream failure)"). Ce n'est pas un défaut du site, c'est une restriction de cet environnement d'exécution — les sections A (disponibilité live) et B (balayage live du sitemap, 83 URLs) n'ont pas pu être exécutées aujourd'hui.
- **DNS : aucun problème.** Résolution via `python3 socket.getaddrinfo` (ne passe pas par le proxy HTTPS bloqué) :
  - `mybusinessnotebook.com` → `216.198.79.1` (plage Vercel)
  - `www.mybusinessnotebook.com` → `66.33.60.193` / `76.76.21.241` (plages Vercel)
  - Pas d'IP de parking Namecheap, pas de nameserver `failed-whois-verification`. DNS correctement pointé vers Vercel.

## CRITIQUE

Aucun problème critique. Sections C, D, E, F (toutes sur disque) exécutées intégralement et ressorties propres. Sections A et B non exécutées (réseau bloqué, voir ci-dessus) — ne pas interpréter cette absence comme une confirmation que le site répond en ligne.

## MOYEN

Aucun problème trouvé :
- **Intégrité des liens internes (disque)** : 83 fichiers `.html` passés en revue (hors `/sw/`, hors fichier de vérification Google), tous les `href`, `src` et `background-image: url(...)` internes vérifiés (liens root-relatifs, relatifs et absolus sur le domaine), plus balises `hreflang` et champs `url`/`@id` en JSON-LD — 0 lien cassé.
- **Piège des URLs sans extension** : 0 URL absolue interne vers un article sans `.html`.
- **Cohérence sitemap.xml** : 83 entrées `<loc>` dans le sitemap, correspondance exacte 1:1 avec les 83 pages sur disque (4 pages d'accueil FR/EN/ES/PT + 79 articles ; fichier de vérification Google exclu des deux côtés). 0 entrée pointant vers un fichier manquant, 0 page présente sur disque et absente du sitemap, 0 doublon.
- **Balises d'en-tête** : les 83 pages contrôlées ont toutes un `title`, une `meta description`, un `canonical`, une `meta robots`, un `og:image`, un `viewport`, et exactement un seul `h1`. 0 page en défaut. 0 `canonical`/`og:url` utilisant `www`.

Nouveauté depuis le dernier contrôle (2026-07-22) : l'article `en/best-pos-system-kenya-duka-2026.html` a été ajouté (Kenya/duka) — carte accueil EN, images et entrée sitemap déjà correctement en place, rien à corriger.

## COSMETIQUE

Aucun problème trouvé :
- 0 carte `pc-ph` (tuile emoji/dégradé) sur les 4 pages d'accueil — toutes les cartes utilisent `pc-media` avec une vraie photo en `background-image`.
- 0 article sans section `related-block` complète (3 liens `post-card` minimum) sur les 79 articles contrôlés.

## CORRIGE AUTOMATIQUEMENT

Aucune correction nécessaire aujourd'hui : toutes les vérifications sur disque (C, D, E, F) sont ressorties propres. Aucun fichier de contenu, sitemap ou tête de page n'a été modifié.
