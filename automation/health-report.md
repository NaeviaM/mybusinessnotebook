# Rapport de sante, 2026-09-26 08:42 UTC

VERIF LIVE : EFFECTUEE

**STATUT GLOBAL : OK**

Controle deterministe, sans modele de langage. Remplace l'agent cloud tombe en panne le 04/08/2026. Declenche chaque jour par la tache planifiee Windows `MBN - controle de sante` (voir C:\Users\dell\mbn-automation).

NB : la section B interroge le sitemap EN LIGNE, elle ne voit donc pas un article encore non deploye. La section D, elle, controle le disque. La section L ne mesure rien d'elle-meme : elle relit le dernier export Search Console, il faut donc le rafraichir a la main.

## A. Disponibilite en direct

- apex : `200`
- www : `200`
- secours Vercel : `200`
- accueil EN : `200`
- accueil ES : `200`
- accueil PT : `200`
- accueil SW : `200`

## B. Balayage du sitemap en direct

- 125 URLs testees, 0 en echec

## C. Liens et images sur disque

- 125 pages controlees, 0 probleme(s)

## D. Coherence du sitemap

- 125 entrees, 125 pages sur disque, 0 manquante(s), 0 orpheline(s)

## E. Balises d'en-tete

- 0 manque(s) de balise

## F. Cosmetique

- 0 tuile(s) emoji, 0 article(s) sans bloc « a lire aussi »

## G. Standards SEO

- 0 ecart(s) aux standards SEO

## H. Coherence des visuels

- 124 familles d'images sur 5 langues, 122 affichees, 2 en reserve
- 0 variante(s) desynchronisee(s), 0 photo(s) empruntee(s) a la reserve, 8 groupe(s) d'articles differents illustres pareil

## I. Ancres internes

- 0 ancre(s) cassee(s), 0 identifiant(s) en double

## J. Reciprocite hreflang

- 125 pages, 0 ecart(s) hreflang

## K. Liens de sources

- 125 liens de sources testes, 0 mort(s), 2 deplace(s), 3 sans reponse, 16 non testable(s) (anti-robot)

## L. Indexation (Search Console)

- au 2026-08-28 : **40 pages dans l'index**, 89 hors index (31 % indexe)
  - Détectée, actuellement non indexée : 68
  - Page avec redirection : 7
  - Autre page avec balise canonique correcte : 7
  - Explorée, actuellement non indexée : 3
- 3 mois : 21 clics, 15614 impressions, CTR 0.13 %
- 85 page(s) jamais vue(s) en recherche sur 125, dont 0 sans aucun lien entrant
- 10 requete(s) en position 11 a 20, a un cran de la page 1 : « candy store pos system » (225 imp, pos 19.5), « chocolate store pos » (186 imp, pos 18.7), « choco store pos » (178 imp, pos 13.8), « pos options for candy store » (165 imp, pos 19.5)

## CRITIQUE

Aucun probleme trouve.

## MOYEN

Aucun probleme trouve.

## DETTE CONNUE (n'affecte pas le statut)

- Meme photo sur des articles qui ne sont pas traductions l'un de l'autre : `calculateur-cout-caisse.html`, `en/cash-flow-management-small-business.html`, `es/alta-sat-resico-pequenos-negocios.html`, `pt/software-faturacao-certificada-portugal.html`
  - _accepte le 2026-09-06 : dedoublonnage du 02/09 : les 13 emplacements servis par la reserve sont faits, ces 7 groupes attendent une image generee, prompts A1 a A10 dans PROMPTS-IMAGES.md_
- Meme photo sur des articles qui ne sont pas traductions l'un de l'autre : `en/best-pos-system-small-business.html`, `logiciel-caisse-epicerie.html`
  - _accepte le 2026-09-06 : dedoublonnage du 02/09 : les 13 emplacements servis par la reserve sont faits, ces 7 groupes attendent une image generee, prompts A1 a A10 dans PROMPTS-IMAGES.md_
- Meme photo sur des articles qui ne sont pas traductions l'un de l'autre : `en/candy-store-pos-system.html`, `es/tpv-para-chocolateria.html`, `logiciel-caisse-chocolaterie.html`, `pt/pdv-para-doceria.html`
  - _accepte le 2026-09-07 : consequence assumee de la separation des grappes du 07/09 : ces quatre pages partageaient une photo parce qu'elles formaient une seule famille de traductions. La page anglaise bonbons et la doceria bresilienne sont desormais une grappe a part, la chocolaterie FR et ES en sont une autre, et la photo de vitrine a pralines n'appartient plus qu'a la seconde. Prompt A11 dans PROMPTS-IMAGES.md pour la photo de confiserie en vrac qui manque aux deux premieres._
- Meme photo sur des articles qui ne sont pas traductions l'un de l'autre : `en/etims-compliant-pos-kenya.html`, `sw/index.html`, `sw/mfumo-wa-pos-kenya.html`
  - _accepte le 2026-09-06 : dedoublonnage du 02/09 : les 13 emplacements servis par la reserve sont faits, ces 7 groupes attendent une image generee, prompts A1 a A10 dans PROMPTS-IMAGES.md_
- Meme photo sur des articles qui ne sont pas traductions l'un de l'autre : `en/hidden-pos-fees.html`, `en/pos-total-cost-calculator.html`
  - _accepte le 2026-09-06 : dedoublonnage du 02/09 : les 13 emplacements servis par la reserve sont faits, ces 7 groupes attendent une image generee, prompts A1 a A10 dans PROMPTS-IMAGES.md_
- Meme photo sur des articles qui ne sont pas traductions l'un de l'autre : `es/tpv-para-fruteria.html`, `logiciel-caisse-primeur.html`, `pt/pdv-para-mercadinho.html`
  - _accepte le 2026-09-06 : dedoublonnage du 02/09 : les 13 emplacements servis par la reserve sont faits, ces 7 groupes attendent une image generee, prompts A1 a A10 dans PROMPTS-IMAGES.md_
- Meme photo sur des articles qui ne sont pas traductions l'un de l'autre : `es/tpv-para-vinoteca.html`, `logiciel-caisse-bar.html`, `pt/pdv-para-adega.html`
  - _accepte le 2026-09-06 : dedoublonnage du 02/09 : les 13 emplacements servis par la reserve sont faits, ces 7 groupes attendent une image generee, prompts A1 a A10 dans PROMPTS-IMAGES.md_
- Meme photo sur des articles qui ne sont pas traductions l'un de l'autre : `pt/calculadora-custo-pdv.html`, `pt/sistema-pdv-nfce-brasil.html`
  - _accepte le 2026-09-06 : dedoublonnage du 02/09 : les 13 emplacements servis par la reserve sont faits, ces 7 groupes attendent une image generee, prompts A1 a A10 dans PROMPTS-IMAGES.md_

## COSMETIQUE

- Source deplacee : https://cfinance.news/index.php/fr/fintech/mobile-money/1420-paiements-instantanes-le-mobile-money-une-nouvelle-caisse-de-confiance-des-commercantes-burkinabe-2 arrive sur https://cfinance.news/article/paiements-instantanes-le-mobile-money-une-nouvelle-caisse-de-confiance-des-commercantes-burkinabe-2/ (`caisse-plusieurs-portefeuilles-mobile-money.html`)
- Source sans reponse (`silence`) au moment du controle, a revoir au prochain passage : https://www.dgid.sn/ (`facture-normalisee-coupure-reseau.html`, `logiciel-caisse-boutique-senegal.html`, `logiciel-caisse-facture-normalisee-afrique-ouest.html`)
- Source deplacee : https://www.ecommercebytes.com/2023/09/08/square-outage-leaves-merchants-unable-to-process-payments/ arrive sur https://ecommercebytes.com/ (`en/pos-outage-what-to-do.html`)
- Source sans reponse (`silence`) au moment du controle, a revoir au prochain passage : https://www.osiris.sn/Code-toxique-faux-agent-telephone.html (`caisse-plusieurs-portefeuilles-mobile-money.html`)
- Source sans reponse (`silence`) au moment du controle, a revoir au prochain passage : https://www.rbz.co.zw/ (`en/dual-currency-pos-zimbabwe.html`)
