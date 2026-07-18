# Rapport de santé — 2026-07-18

**STATUT GLOBAL : DEGRADE**

## ACTION REQUISE UTILISATEUR

- **Vérification live impossible depuis cet environnement.** Le proxy sortant du bac à sable (agent proxy, port 39319) a refusé toutes les connexions HTTPS vers `mybusinessnotebook.com`, `www.mybusinessnotebook.com` ET le fallback `le-carnet-du-commercant.vercel.app` avec un `403 Forbidden` au niveau du tunnel CONNECT (motif rapporté par le proxy : `connect_rejected` / « policy denial »). Testé avec `curl` et avec l'outil `WebFetch` : même résultat sur les deux. Ce n'est PAS une preuve que le site est en panne — c'est une restriction réseau de cet environnement d'exécution qui empêche toute vérification live (sections A et B du contrôle) aujourd'hui.
  - Aucune action possible côté code pour contourner ce blocage (interdiction explicite de retenter ou de désactiver la vérification TLS/le proxy).
  - Pour que les prochains health-checks automatiques puissent réellement tester le site en ligne, il faut que l'environnement (ou son administrateur) autorise la sortie réseau vers `mybusinessnotebook.com`, `www.mybusinessnotebook.com` et `*.vercel.app` dans la politique du proxy sortant.
- **DNS : PAS de problème détecté.** La résolution DNS (via `python3 socket.getaddrinfo`, qui ne passe pas par le proxy HTTPS bloqué) donne :
  - `mybusinessnotebook.com` → `216.198.79.1` (plage Vercel actuelle)
  - `www.mybusinessnotebook.com` → `76.76.21.98` / `66.33.60.67` (plages Vercel)
  - Ces adresses correspondent à l'infrastructure Vercel (à comparer avec `cname.vercel-dns.com` → `76.76.21.142` / `66.33.60.66`, mêmes plages), pas à une IP de parking Namecheap. Le DNS semble donc correctement pointé vers Vercel ; aucune correction chez le registrar n'est identifiée comme nécessaire aujourd'hui. (Seule la couche HTTP n'a pas pu être testée, voir point ci-dessus.)

## CRITIQUE

Aucun problème critique détecté dans les vérifications qui ont pu être exécutées (sections C, D, E, F — toutes sur disque). Les sections A (disponibilité live) et B (balayage live du sitemap, ~78 URLs) n'ont PAS pu être exécutées du tout (voir ACTION REQUISE UTILISATEUR) : ne pas interpréter cette absence de résultat comme une confirmation que le site fonctionne.

## MOYEN

Aucun problème trouvé :
- **Intégrité des liens internes (disque)** : 79 fichiers `.html` passés en revue (hors `/sw/`), tous les `href`, `src` et `background-image: url(...)` internes résolus — 0 lien cassé.
- **Piège des URLs sans extension** : 0 URL absolue interne vers un article sans `.html` trouvée.
- **Cohérence sitemap.xml** : 78 entrées dans le sitemap, correspondance exacte 1:1 avec les 78 fichiers articles/homepages sur disque (24 FR dont l'accueil, 20 EN dont l'accueil, 16 ES dont l'accueil, 19 PT dont l'accueil, moins le fichier de vérification Google exclu). 0 entrée pointant vers un fichier manquant, 0 article présent sur disque et absent du sitemap.
- **Balises d'en-tête** : les 78 pages contrôlées ont toutes un `title`, une `meta description`, un `canonical`, une `meta robots`, un `viewport`, et exactement un seul `h1`. 0 page en défaut.

## COSMETIQUE

Aucun problème trouvé : 0 carte `pc-ph` (tuile emoji/dégradé) sur les 4 pages d'accueil — toutes les cartes utilisent `pc-media` avec une vraie photo (`index.html` : 19 cartes ; `en/index.html` : 19 ; `es/index.html` : 15 ; `pt/index.html` : 18).

## CORRIGE AUTOMATIQUEMENT

Aucune correction nécessaire : toutes les vérifications sur disque (C, D, E, F) sont ressorties propres. Aucun fichier de contenu, sitemap ou tête de page n'a été modifié.
