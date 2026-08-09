# Rapport de sante, 2026-08-09 02:21 UTC

VERIF LIVE : EFFECTUEE

**STATUT GLOBAL : CRITIQUE**

Controle deterministe, sans modele de langage. Remplace l'agent cloud tombe en panne le 04/08/2026. Declenche par `.github/workflows/health-check.yml` une fois ce fichier present sur le depot, sinon lance a la main.

NB : la section B interroge le sitemap EN LIGNE, elle ne voit donc pas un article encore non deploye. La section D, elle, controle le disque.

## A. Disponibilite en direct

- apex : `200`
- www : `200`
- secours Vercel : `200`
- accueil EN : `200`
- accueil ES : `200`
- accueil PT : `200`

## B. Balayage du sitemap en direct

- 96 URLs testees, 3 en echec

## C. Liens et images sur disque

- 97 pages controlees, 0 probleme(s)

## D. Coherence du sitemap

- 97 entrees, 97 pages sur disque, 0 manquante(s), 0 orpheline(s)

## E. Balises d'en-tete

- 0 manque(s) de balise

## F. Cosmetique

- 0 tuile(s) emoji, 0 article(s) sans bloc « a lire aussi »

## CRITIQUE

- URL du sitemap en erreur `0` : https://mybusinessnotebook.com/es/calculadora-coste-tpv.html
- URL du sitemap en erreur `0` : https://mybusinessnotebook.com/pt/calculadora-custo-pdv.html
- URL du sitemap en erreur `0` : https://mybusinessnotebook.com/en/vat-threshold-uk-shop-owners.html

## MOYEN

Aucun probleme trouve.

## COSMETIQUE

Aucun probleme trouve.
