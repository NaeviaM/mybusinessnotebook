# Rapport de sante, 2026-10-04 07:30 UTC

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

- 146 URLs testees, 0 en echec

## C. Liens et images sur disque

- 146 pages controlees, 0 probleme(s)

## D. Coherence du sitemap

- 146 entrees, 146 pages sur disque, 0 manquante(s), 0 orpheline(s)

## E. Balises d'en-tete

- 0 manque(s) de balise

## F. Cosmetique

- 0 tuile(s) emoji, 0 article(s) sans bloc « a lire aussi »

## G. Standards SEO

- 0 ecart(s) aux standards SEO

## H. Coherence des visuels

- 145 familles d'images sur 5 langues, 143 affichees, 2 en reserve
- 0 variante(s) desynchronisee(s), 0 photo(s) empruntee(s) a la reserve, 8 groupe(s) d'articles differents illustres pareil

## I. Ancres internes

- 0 ancre(s) cassee(s), 0 identifiant(s) en double

## J. Reciprocite hreflang

- 146 pages, 0 ecart(s) hreflang

## K. Liens de sources

- 262 liens de sources testes, 0 mort(s), 8 deplace(s), 12 sans reponse, 20 non testable(s) (anti-robot)

## L. Indexation (Search Console)

- au 2026-08-28 : **40 pages dans l'index**, 89 hors index (31 % indexe)
  - Détectée, actuellement non indexée : 68
  - Page avec redirection : 7
  - Autre page avec balise canonique correcte : 7
  - Explorée, actuellement non indexée : 3
- 3 mois : 21 clics, 15614 impressions, CTR 0.13 %
- 106 page(s) jamais vue(s) en recherche sur 146, dont 0 sans aucun lien entrant
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

- Source deplacee : https://asic.gov.au/for-business/registering-a-business-name/ arrive sur https://www.asic.gov.au/for-business-and-companies/business-names/register-a-business-name (`en/got-your-abn-get-first-customers.html`)
- Source deplacee : https://cfinance.news/index.php/fr/fintech/mobile-money/1420-paiements-instantanes-le-mobile-money-une-nouvelle-caisse-de-confiance-des-commercantes-burkinabe-2 arrive sur https://cfinance.news/article/paiements-instantanes-le-mobile-money-une-nouvelle-caisse-de-confiance-des-commercantes-burkinabe-2/ (`caisse-plusieurs-portefeuilles-mobile-money.html`)
- Source sans reponse (`400`) au moment du controle, a revoir au prochain passage : https://faq.whatsapp.com/1791149784551042/?locale=pt_PT (`pt/divulgar-negocio-google-instagram-whatsapp.html`)
- Source sans reponse (`400`) au moment du controle, a revoir au prochain passage : https://faq.whatsapp.com/2565868990219715/?locale=pt_PT (`pt/divulgar-negocio-google-instagram-whatsapp.html`)
- Source sans reponse (`400`) au moment du controle, a revoir au prochain passage : https://faq.whatsapp.com/405903568419894/?locale=pt_PT (`pt/divulgar-negocio-google-instagram-whatsapp.html`)
- Source sans reponse (`400`) au moment du controle, a revoir au prochain passage : https://faq.whatsapp.com/502291734918768/?locale=pt_PT (`pt/divulgar-negocio-google-instagram-whatsapp.html`)
- Source sans reponse (`400`) au moment du controle, a revoir au prochain passage : https://faq.whatsapp.com/577829787429875/?locale=pt_PT (`pt/divulgar-negocio-google-instagram-whatsapp.html`)
- Source sans reponse (`400`) au moment du controle, a revoir au prochain passage : https://faq.whatsapp.com/641572844337957/?locale=pt_PT (`pt/divulgar-negocio-google-instagram-whatsapp.html`)
- Source sans reponse (`400`) au moment du controle, a revoir au prochain passage : https://faq.whatsapp.com/647574060315065/?locale=pt_PT (`pt/divulgar-negocio-google-instagram-whatsapp.html`)
- Source sans reponse (`silence`) au moment du controle, a revoir au prochain passage : https://www.abr.gov.au/business-super-funds-charities/applying-abn (`en/got-your-abn-get-first-customers.html`)
- Source sans reponse (`silence`) au moment du controle, a revoir au prochain passage : https://www.acma.gov.au/avoid-sending-spam (`en/got-your-abn-get-first-customers.html`)
- Source sans reponse (`silence`) au moment du controle, a revoir au prochain passage : https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/gst-hst-businesses/when-register-charge.html (`en/sole-proprietorship-canada-first-customers.html`)
- Source sans reponse (`silence`) au moment du controle, a revoir au prochain passage : https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/registering-your-business/you-need-a-business-number-a-program-account.html (`en/sole-proprietorship-canada-first-customers.html`)
- Source deplacee : https://www.cnil.fr/fr/la-prospection-commerciale-par-courrier-electronique arrive sur https://www.cnil.fr/fr/la-prospection-commerciale-par-courrier-electronique-sms-mms-et-automate-dappel (`se-faire-connaitre-ouverture-entreprise.html`, `trouver-clients-auto-entrepreneur-sans-reseau.html`, `trouver-des-clients-avec-ia.html`)
- Source sans reponse (`silence`) au moment du controle, a revoir au prochain passage : https://www.dgid.sn/ (`facture-normalisee-coupure-reseau.html`, `logiciel-caisse-boutique-senegal.html`, `logiciel-caisse-facture-normalisee-afrique-ouest.html`)
- Source deplacee : https://www.ecommercebytes.com/2023/09/08/square-outage-leaves-merchants-unable-to-process-payments/ arrive sur https://ecommercebytes.com/ (`en/pos-outage-what-to-do.html`)
- Source deplacee : https://www.gov.uk/government/publications/fake-reviews-cma208 arrive sur https://www.gov.uk/government/publications/fake-reviews (`en/advertise-business-locally-free-uk.html`)
- Source deplacee : https://www.gov.uk/register-for-self-assessment/self-employed arrive sur https://www.gov.uk/register-for-self-assessment (`en/sole-trader-how-to-get-customers.html`)
- Source deplacee : https://www.gov.uk/set-up-sole-trader arrive sur https://www.gov.uk/become-sole-trader (`en/sole-trader-how-to-get-customers.html`)
- Source deplacee : https://www.sba.gov/business-guide/manage-your-business/marketing-sales arrive sur https://www.sba.gov/counseling/manage-your-business/#marketing-and-sales (`en/how-to-get-your-new-business-noticed.html`, `en/how-to-market-a-small-business-locally.html`)
- Resume Search Console vieux de 28 jours : retelecharger les exports et relancer `python automation/gsc_import.py`.
