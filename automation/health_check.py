#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controle de sante quotidien de My Business Notebook.

Remplace l'agent cloud "daily health check", tombe en panne le 04/08/2026.
Aucun modele de langage n'est necessaire : tous les controles sont deterministes.
Avantage sur l'ancien agent : GitHub Actions a un vrai acces reseau sortant, donc
la verification EN DIRECT est enfin possible (le bac a sable cloud la bloquait).

Une seule dependance, optionnelle : Pillow, pour la section H (coherence des
visuels). Si elle manque, la section est sautee et signalee, rien ne casse.

Ecrit automation/health-report.md, ajoute une ligne a automation/health-history.log,
et sort en code 1 si un probleme CRITIQUE est trouve.
"""
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://mybusinessnotebook.com"
FALLBACK = "https://le-carnet-du-commercant.vercel.app"
UA = "MBN-health-check/1.0 (+https://mybusinessnotebook.com)"
LANGS = {"fr": ROOT, "en": ROOT / "en", "es": ROOT / "es", "pt": ROOT / "pt", "sw": ROOT / "sw"}
# 404.html est volontairement en noindex et sans canonical : la controler ferait
# remonter de faux manques de balises. Le fichier de verification Google non plus.
SKIP = {"google5f267a48e7657a47.html", "404.html"}

critique, moyen, cosmetique = [], [], []


def http(url, method="GET", timeout=25):
    """Renvoie (code, corps). Code 0 si la requete n'aboutit pas."""
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace") if method == "GET" else ""
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def pages(d):
    return [p for p in sorted(d.glob("*.html")) if p.name not in SKIP]


# ---------------------------------------------------------------- A. disponibilite
def reseau_present():
    """La machine a-t-elle un acces sortant ? Teste deux hotes tiers tres stables.

    Le 18/08/2026, le PC a perdu sa connexion pendant le controle : les six URLs
    ont repondu `0` et le rapport a declare le site MORT alors qu'il etait debout.
    Un code 0 ne distingue pas un site en panne d'une machine hors ligne, donc on
    tranche ici avant d'accuser le site.
    """
    for sonde in ("https://www.google.com/generate_204", "https://one.one.one.one/"):
        code, _ = http(sonde, "HEAD", timeout=10)
        if code:
            return True
    return False


def section_a():
    lignes = []
    en_ligne = reseau_present()
    if not en_ligne:
        moyen.append("Machine sans acces reseau : la disponibilite du site n'a PAS pu "
                     "etre verifiee. Ce n'est pas une panne du site.")
        return ["- Machine hors ligne, verification impossible (aucune conclusion sur le site)."]
    for label, url in [("apex", BASE + "/"), ("www", "https://www.mybusinessnotebook.com/"),
                       ("secours Vercel", FALLBACK + "/"),
                       ("accueil EN", BASE + "/en/"), ("accueil ES", BASE + "/es/"),
                       ("accueil PT", BASE + "/pt/"), ("accueil SW", BASE + "/sw/")]:
        code, _ = http(url, "HEAD")
        lignes.append(f"- {label} : `{code}`")
        if label == "apex" and code != 200:
            critique.append(f"L'accueil ne repond pas : `{code}` sur {url}.")
        elif label.startswith("accueil") and code != 200:
            critique.append(f"{label} ne repond pas : `{code}`.")
    return lignes


# ------------------------------------------------------------- B. balayage en direct
def section_b():
    code, xml = http(BASE + "/sitemap.xml")
    if code == 0:
        # Code 0 = la requete n'est jamais partie. Reseau local, pas le site.
        moyen.append("sitemap.xml non joignable depuis cette machine (reseau local).")
        return ["- Reseau indisponible, balayage impossible (aucune conclusion sur le site)."], []
    if code != 200:
        critique.append(f"sitemap.xml inaccessible en ligne (`{code}`).")
        return ["- sitemap.xml inaccessible, balayage impossible"], []
    urls = re.findall(r"<loc>([^<]+)</loc>", xml)
    echecs = []
    for u in urls:
        c, _ = http(u, "HEAD")
        if c != 200:
            echecs.append((c, u))
    for c, u in echecs:
        critique.append(f"URL du sitemap en erreur `{c}` : {u}")
    return [f"- {len(urls)} URLs testees, {len(echecs)} en echec"], urls


# ------------------------------------------------ C. liens internes et images (disque)
def section_c():
    casses = 0
    externe = re.compile(r"^(?:https?:|//|#|\?|mailto:|tel:|data:)")
    for lg, d in LANGS.items():
        for p in pages(d):
            s = p.read_text(encoding="utf-8")
            cibles = re.findall(r'href="([^"]+\.html)"', s)
            cibles += re.findall(r'(?:src="|background-image:\s*url\(\')([^"\')]+\.(?:webp|jpg|png|svg))', s)
            for t in cibles:
                if externe.match(t):          # lien absolu ou ancre, pas un fichier local
                    continue
                # Un href qui commence par "/" est relatif a la racine du site, pas au
                # dossier de la langue : le resoudre depuis `d` inventait des liens casses.
                cible = (ROOT / t.lstrip("/")) if t.startswith("/") else (d / t)
                if not cible.exists():
                    critique.append(f"Lien ou image casse dans `{p.relative_to(ROOT)}` : `{t}`")
                    casses += 1
            # le piege connu : une URL absolue d'article qui oublie le .html renvoie 404.
            # Les accueils de langue (/ /en/ /es/ /pt/) en sont exemptes.
            for u in re.findall(r'https://mybusinessnotebook\.com/([^"\'\s>]*)', s):
                if not u or u.endswith("/") or u in ("en", "es", "pt", "sw"):
                    continue
                if "." not in u.rsplit("/", 1)[-1]:
                    critique.append(f"URL absolue sans `.html` dans `{p.relative_to(ROOT)}` : `/{u}`")
                    casses += 1
    return [f"- {sum(len(pages(d)) for d in LANGS.values())} pages controlees, {casses} probleme(s)"]


# ------------------------------------------------------------- D. coherence du sitemap
def section_d():
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    dans = set(re.findall(r"<loc>https://mybusinessnotebook\.com/([^<]*)</loc>", sm))
    sur_disque = set()
    for lg, d in LANGS.items():
        prefixe = "" if lg == "fr" else f"{lg}/"
        for p in pages(d):
            sur_disque.add(prefixe if p.name == "index.html" else prefixe + p.name)
    for m in sorted(sur_disque - dans):
        moyen.append(f"Page absente du sitemap : `{m}`")
    for m in sorted(dans - sur_disque):
        critique.append(f"Entree de sitemap sans fichier : `{m}`")
    return [f"- {len(dans)} entrees, {len(sur_disque)} pages sur disque, "
            f"{len(sur_disque - dans)} manquante(s), {len(dans - sur_disque)} orpheline(s)"]


# --------------------------------------------------------------------- E. balises head
def section_e():
    manques = 0
    for lg, d in LANGS.items():
        for p in pages(d):
            s = p.read_text(encoding="utf-8")
            for balise, motif in [("title", r"<title>[^<]+</title>"),
                                  ("meta description", r'<meta name="description" content="[^"]+"'),
                                  ("canonical", r'rel="canonical"'),
                                  ("meta robots", r'<meta name="robots"'),
                                  ("og:image", r'property="og:image"'),
                                  ("viewport", r'name="viewport"')]:
                if not re.search(motif, s):
                    moyen.append(f"`{p.relative_to(ROOT)}` sans {balise}")
                    manques += 1
            n = len(re.findall(r"<h1[ >]", s))
            if n != 1:
                moyen.append(f"`{p.relative_to(ROOT)}` a {n} balises h1")
                manques += 1
            if re.search(r'(?:canonical|og:url)[^>]*www\.mybusinessnotebook', s):
                critique.append(f"`{p.relative_to(ROOT)}` utilise www dans son canonical")
                manques += 1
    return [f"- {manques} manque(s) de balise"]


# ------------------------------------------------------------------------ F. cosmetique
def section_f():
    ph = sum(len(re.findall(r'class="pc-ph"', (d / "index.html").read_text(encoding="utf-8")))
             for d in LANGS.values() if (d / "index.html").exists())
    if ph:
        cosmetique.append(f"{ph} carte(s) d'accueil encore en tuile emoji `pc-ph`")
    sans = [f"{p.relative_to(ROOT)}" for d in LANGS.values() for p in pages(d)
            if p.name != "index.html" and "related-block" not in p.read_text(encoding="utf-8")]
    for s in sans:
        cosmetique.append(f"`{s}` sans bloc « a lire aussi »")
    return [f"- {ph} tuile(s) emoji, {len(sans)} article(s) sans bloc « a lire aussi »"]


# ------------------------------------------------------------------------ G. SEO
def section_g():
    """Standards fixes le 21/08/2026 apres l'audit SEO complet du site.

    Chacun de ces points manquait sur la quasi-totalite des pages et a ete corrige
    en une passe. Ils sont controles ici pour que le publieur ne les reperde pas
    article apres article : le brief les impose, cette section le verifie.
    """
    import json as _json
    ecarts = 0
    for lg, d in LANGS.items():
        for p in pages(d):
            nom = p.relative_to(ROOT)
            s = p.read_text(encoding="utf-8")
            tete = s.split("</head>")[0]

            t = re.search(r"<title[^>]*>(.*?)</title>", tete, re.S)
            if t and len(t.group(1).strip()) > 62:
                moyen.append(f"`{nom}` : titre de {len(t.group(1).strip())} caracteres, coupe dans les resultats (max 60)")
                ecarts += 1

            m = re.search(r'<meta name="description" content="([^"]*)"', tete)
            if m:
                n = len(m.group(1))
                if n > 165:
                    moyen.append(f"`{nom}` : meta description de {n} caracteres, coupee (max 158)")
                    ecarts += 1
                elif n < 90:
                    cosmetique.append(f"`{nom}` : meta description de {n} caracteres, trop courte")

            can = re.search(r'<link rel="canonical" href="([^"]+)"', tete)
            ogu = re.search(r'<meta property="og:url" content="([^"]+)"', tete)
            if not ogu:
                moyen.append(f"`{nom}` sans og:url")
                ecarts += 1
            elif can and ogu.group(1) != can.group(1):
                moyen.append(f"`{nom}` : og:url et canonical ne coincident pas")
                ecarts += 1

            for tag in ("twitter:card", "twitter:title", "twitter:description", "twitter:image"):
                if f'name="{tag}"' not in tete:
                    cosmetique.append(f"`{nom}` sans {tag}")

            # Un lien commercial non qualifie expose le site a une penalite liens.
            for lien in re.findall(r"<a[^>]*digablopos[^>]*>", s, re.I):
                if "sponsored" not in lien:
                    moyen.append(f"`{nom}` : lien vers digablopos.fr sans rel=sponsored")
                    ecarts += 1
                    break

            for bloc in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
                try:
                    noeud = _json.loads(bloc)
                except Exception:
                    critique.append(f"`{nom}` : JSON-LD invalide, aucun resultat enrichi possible")
                    ecarts += 1
                    continue
                for n2 in (noeud if isinstance(noeud, list) else [noeud]):
                    if isinstance(n2, dict) and n2.get("@type") in ("Article", "BlogPosting"):
                        for champ in ("image", "description", "dateModified", "mainEntityOfPage", "publisher"):
                            if champ not in n2:
                                moyen.append(f"`{nom}` : schema Article sans {champ}")
                                ecarts += 1
    return [f"- {ecarts} ecart(s) aux standards SEO"]


# ------------------------------------------------------- H. coherence des visuels
# Ajoutee le 21/08/2026, apres le cas `logiciel-caisse-boutique-cote-ivoire` : la
# photo d'en-tete avait ete remplacee (un cafe occidental, prix en dollars, ne
# collait pas a un article ivoirien) mais la vignette -sm.webp etait restee sur
# l'ancienne image pendant neuf jours. Personne ne l'a vu parce que la vignette
# n'est appelee que depuis l'accueil, jamais depuis l'article : en relisant la page
# corrigee, tout paraissait juste. Les sections C et E ne pouvaient pas l'attraper,
# elles verifient qu'un fichier existe et qu'une balise est la, pas ce que l'image
# montre.
#
# On compare donc le CONTENU des variantes d'un meme article, via une empreinte
# perceptuelle (dHash 64 bits, insensible au redimensionnement et a la
# recompression). Mesure sur les 35 familles du site au moment de l'ajout :
# variantes d'une meme photo, ecart 0 ou 1 ; photos differentes, 18 au minimum ;
# le cas ivoirien etait a 37. Le seuil de 10 laisse une marge large des deux cotes.
SEUIL_VARIANTE = 10


def _empreinte(chemin):
    """dHash 8x8 : 64 bits qui decrivent la forme de l'image, pas ses octets.

    Chaque bit dit si un pixel est plus clair que son voisin de droite. Deux
    encodages d'une meme photo donnent la meme empreinte ; deux photos
    differentes divergent tres vite.
    """
    from PIL import Image
    im = Image.open(chemin).convert("L").resize((9, 8), Image.LANCZOS)
    px = im.tobytes()
    bits = 0
    for r in range(8):
        ligne = px[r * 9:(r + 1) * 9]
        for c in range(8):
            bits = (bits << 1) | (1 if ligne[c] > ligne[c + 1] else 0)
    return bits


def _ecart(a, b):
    """Distance de Hamming entre deux empreintes : 0 = identiques, 64 = opposees."""
    return bin(a ^ b).count("1")


def section_h():
    dossier = ROOT / "img"
    if not dossier.is_dir():
        return ["- Aucun dossier `img/`."]
    try:
        import PIL  # noqa: F401
    except ImportError:
        # Jamais bloquant : ce script est le garde-fou qui autorise la publication.
        # Il ne doit pas tomber parce qu'une dependance optionnelle manque.
        cosmetique.append("Coherence des visuels non controlee : Pillow absent (`pip install Pillow`)")
        return ["- Sautee : Pillow n'est pas installe."]

    familles = {}
    for p in sorted(dossier.iterdir()):
        if not p.is_file():
            continue
        m = re.match(r"^(.+?)(-sm)?\.(jpg|jpeg|png|webp)$", p.name, re.I)
        if m:
            familles.setdefault(m.group(1), {})[p.name] = p

    ecarts, refs = 0, {}
    for base, variantes in sorted(familles.items()):
        try:
            empreintes = {nom: _empreinte(p) for nom, p in variantes.items()}
        except Exception as e:
            moyen.append(f"Image illisible dans la famille `{base}` : {e}")
            ecarts += 1
            continue
        # La grande image fait foi : c'est celle qu'on remplace a la main, la
        # vignette n'est qu'un derive qu'on oublie de regenerer.
        principale = next((n for n in (f"{base}.jpg", f"{base}.jpeg", f"{base}.webp")
                           if n in empreintes), sorted(empreintes)[0])
        refs[base] = empreintes[principale]
        for nom in sorted(empreintes):
            d = _ecart(empreintes[principale], empreintes[nom])
            if d > SEUIL_VARIANTE:
                moyen.append(f"`img/{nom}` ne montre pas la meme photo que `img/{principale}` "
                             f"(ecart {d}) : variante oubliee lors d'un remplacement")
                ecarts += 1

    # Meme photo sur plusieurs articles : pas une panne, mais le brief demande
    # d'eviter les doublons, et deux articles voisins illustres pareil se voient
    # sur l'accueil. Comparaison exacte : on ne signale que les vrais jumeaux.
    #
    # Restreint aux images REELLEMENT affichees quelque part. Le dossier img/ sert
    # aussi de reserve de photos libres dans laquelle le publieur pioche en copiant
    # le fichier : une photo de reserve est donc le jumeau normal de l'article qui
    # l'a prise, et la signaler ferait un faux positif a chaque publication.
    citees = set()
    for d in LANGS.values():
        for page in pages(d):
            citees.update(re.findall(r"img/([A-Za-z0-9._-]+?)(?:-sm)?\.(?:jpg|jpeg|png|webp)",
                                     page.read_text(encoding="utf-8")))
    par_empreinte = {}
    for base, h in refs.items():
        if base in citees:
            par_empreinte.setdefault(h, []).append(base)
    partages = sorted([sorted(v) for v in par_empreinte.values() if len(v) > 1])
    for groupe in partages:
        cosmetique.append(f"Meme photo sur {len(groupe)} articles : "
                          + ", ".join(f"`{b}`" for b in groupe))

    affichees = citees & set(familles)
    return [f"- {len(familles)} familles d'images dont {len(affichees)} affichees, "
            f"{ecarts} variante(s) desynchronisee(s), "
            f"{len(partages)} photo(s) partagee(s) par plusieurs articles"]


def main():
    # --disk-only : saute les deux sections qui sortent sur le reseau. Sert au
    # publieur local, qui doit pouvoir valider un article meme si la machine est
    # hors ligne ou si le site repond mal au moment ou il tourne.
    disk_only = "--disk-only" in sys.argv
    maintenant = datetime.now(timezone.utc)
    if disk_only:
        a = ["- Sautee (mode --disk-only)."]
        b = ["- Sautee (mode --disk-only)."]
    else:
        a = section_a()
        b, _ = section_b()
    c, d, e, f = section_c(), section_d(), section_e(), section_f()
    g = section_g()
    h = section_h()

    statut = "CRITIQUE" if critique else ("DEGRADE" if moyen else "OK")

    def bloc(titre, items):
        if not items:
            return f"## {titre}\n\nAucun probleme trouve.\n"
        return f"## {titre}\n\n" + "\n".join(f"- {x}" for x in items[:40]) + \
               (f"\n- ... et {len(items)-40} autre(s)\n" if len(items) > 40 else "\n")

    rapport = (
        f"# Rapport de sante, {maintenant:%Y-%m-%d %H:%M} UTC\n\n"
        f"VERIF LIVE : {'IMPOSSIBLE (mode --disk-only)' if disk_only else 'EFFECTUEE'}\n\n"
        f"**STATUT GLOBAL : {statut}**\n\n"
        f"Controle deterministe, sans modele de langage. Remplace l'agent cloud "
        f"tombe en panne le 04/08/2026. Declenche chaque jour par la tache planifiee "
        f"Windows `MBN - controle de sante` (voir C:\\Users\\dell\\mbn-automation).\n\n"
        f"NB : la section B interroge le sitemap EN LIGNE, elle ne voit donc pas "
        f"un article encore non deploye. La section D, elle, controle le disque.\n\n"
        f"## A. Disponibilite en direct\n\n" + "\n".join(a) + "\n\n"
        f"## B. Balayage du sitemap en direct\n\n" + "\n".join(b) + "\n\n"
        f"## C. Liens et images sur disque\n\n" + "\n".join(c) + "\n\n"
        f"## D. Coherence du sitemap\n\n" + "\n".join(d) + "\n\n"
        f"## E. Balises d'en-tete\n\n" + "\n".join(e) + "\n\n"
        f"## F. Cosmetique\n\n" + "\n".join(f) + "\n\n"
        f"## G. Standards SEO\n\n" + "\n".join(g) + "\n\n"
        f"## H. Coherence des visuels\n\n" + "\n".join(h) + "\n\n"
        + bloc("CRITIQUE", critique) + "\n" + bloc("MOYEN", moyen) + "\n" + bloc("COSMETIQUE", cosmetique)
    )

    (ROOT / "automation" / "health-report.md").write_text(rapport, encoding="utf-8")
    with (ROOT / "automation" / "health-history.log").open("a", encoding="utf-8") as h:
        h.write(f"{maintenant:%Y-%m-%d} | {statut} | {len(critique)} problemes critiques | 0 corriges\n")

    print(f"STATUT {statut} | critiques {len(critique)} | moyens {len(moyen)} | cosmetiques {len(cosmetique)}")
    for x in critique[:10]:
        print("  CRITIQUE:", x)
    return 1 if critique else 0


if __name__ == "__main__":
    sys.exit(main())
