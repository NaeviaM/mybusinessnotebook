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
import time
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
def photos_attendues():
    """Slugs dont la photo est commandee (prompt ecrit) mais pas encore generee.

    Le circuit est fixe : la redaction ecrit le prompt dans PROMPTS-IMAGES.md,
    l'utilisateur genere l'image et la depose, elle est ensuite redimensionnee
    et posee au bon slug. Entre les deux, l'article est complet et la page
    s'affiche avec le degrade de secours : ce n'est pas un lien casse, c'est une
    photo en attente. La distinguer evite de noyer les vrais liens casses.
    """
    f = ROOT / "automation" / "photos-attendues.txt"
    if not f.is_file():
        return set()
    slugs = set()
    for ligne in f.read_text(encoding="utf-8").splitlines():
        ligne = ligne.split("#")[0].strip()
        if ligne:
            slugs.add(ligne)
    return slugs


def section_c():
    casses = 0
    attendues = photos_attendues()
    en_attente = set()
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
                    slug = re.sub(r"(-sm)?\.(webp|jpg|jpeg|png|svg)$", "",
                                  cible.resolve().relative_to(ROOT.resolve()).as_posix())
                    if slug in attendues:
                        en_attente.add(slug)
                        continue
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
    for slug in sorted(en_attente):
        moyen.append(f"Photo commandee mais pas encore generee : `{slug}` "
                     f"(prompt ecrit dans PROMPTS-IMAGES.md)")
    lignes = [f"- {sum(len(pages(d)) for d in LANGS.values())} pages controlees, {casses} probleme(s)"]
    if en_attente:
        lignes.append(f"- {len(en_attente)} photo(s) commandee(s), en attente de generation")
    return lignes


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


def _hero(page):
    """Slug de la photo d'en-tete annoncee par la page (og:image)."""
    html = page.read_text(encoding="utf-8", errors="ignore")
    m = (re.search(r'property="og:image"\s+content="([^"]+)"', html)
         or re.search(r'content="([^"]+)"\s+property="og:image"', html))
    if not m:
        return None
    return re.sub(r"\.(jpg|jpeg|png|webp)$", "", m.group(1).rsplit("/", 1)[-1], flags=re.I)


def _alternates(page):
    """Noms de fichier des traductions declarees par la page (hreflang)."""
    html = page.read_text(encoding="utf-8", errors="ignore")
    return {u.rstrip("/").rsplit("/", 1)[-1] or "index.html"
            for u in re.findall(r'rel="alternate"[^>]*href="([^"]+)"', html)}


def section_h():
    """Coherence des visuels, sur TOUTES les langues.

    Trois controles :
      1. variantes d'une meme famille (jpg / webp / -sm) desynchronisees ;
      2. photo empruntee a la reserve : le fichier porte le slug de l'article
         mais montre pixel pour pixel une photo de reserve destinee a un autre
         sujet. C'est ainsi qu'un guide sur le dollar a Kinshasa s'est retrouve
         illustre par une quincaillerie occidentale : le publieur copie un
         fichier de reserve sous le nom du nouvel article, et l'ancien controle,
         qui ne comparait que les noms, n'y voyait rien ;
      3. meme photo sur des articles differents. Deux traductions d'un meme
         article ont normalement la meme photo : on ne les signale donc que si
         elles ne se declarent pas mutuellement en hreflang.

    Le 30/08/2026 cette section ne regardait que `img/` a la racine : les 83
    photos de en/, es/, pt/ et sw/ n'etaient controlees par personne.
    """
    try:
        import PIL  # noqa: F401
    except ImportError:
        # Jamais bloquant : ce script est le garde-fou qui autorise la publication.
        # Il ne doit pas tomber parce qu'une dependance optionnelle manque.
        cosmetique.append("Coherence des visuels non controlee : Pillow absent (`pip install Pillow`)")
        return ["- Sautee : Pillow n'est pas installe."]

    # 1) toutes les familles, toutes langues confondues. Cle = "en/img/mon-slug".
    familles, ecarts = {}, 0
    for lang, d in LANGS.items():
        dossier = d / "img"
        if not dossier.is_dir():
            continue
        par_base = {}
        for p in sorted(dossier.iterdir()):
            if not p.is_file():
                continue
            m = re.match(r"^(.+?)(-sm)?\.(jpg|jpeg|png|webp)$", p.name, re.I)
            if m:
                par_base.setdefault(m.group(1), {})[p.name] = p
        for base, variantes in sorted(par_base.items()):
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
            rel = "img" if lang == "fr" else f"{lang}/img"
            for nom in sorted(empreintes):
                d2 = _ecart(empreintes[principale], empreintes[nom])
                if d2 > SEUIL_VARIANTE:
                    moyen.append(f"`{rel}/{nom}` ne montre pas la meme photo que `{rel}/{principale}` "
                                 f"(ecart {d2}) : variante oubliee lors d'un remplacement")
                    ecarts += 1
            familles[f"{rel}/{base}"] = {"lang": lang, "base": base,
                                         "empreinte": empreintes[principale]}

    # 2) quelle page affiche quelle famille
    heros = {}
    for lang, d in LANGS.items():
        rel_img = "img" if lang == "fr" else f"{lang}/img"
        for page in pages(d):
            base = _hero(page)
            if not base:
                continue
            cle = f"{rel_img}/{base}"
            if cle in familles:
                nom = page.name if lang == "fr" else f"{lang}/{page.name}"
                heros[nom] = {"famille": cle, "empreinte": familles[cle]["empreinte"],
                              "alternates": _alternates(page)}

    utilisees = {v["famille"] for v in heros.values()}
    reserve = {k: v for k, v in familles.items() if k not in utilisees}

    # 3) photo empruntee a la reserve
    empruntes = []
    for nom, info in sorted(heros.items()):
        for k, v in sorted(reserve.items()):
            if _ecart(info["empreinte"], v["empreinte"]) <= SEUIL_VARIANTE:
                empruntes.append((nom, info["famille"], k))
                critique.append(
                    f"`{nom}` affiche `{info['famille']}`, qui est la photo de reserve "
                    f"`{k}` copiee sous un autre nom : l'illustration ne correspond pas au sujet")
                break

    # 4) meme photo sur des articles differents
    groupes, vus = [], set()
    noms = sorted(heros)
    for i, a in enumerate(noms):
        if a in vus:
            continue
        groupe = [a]
        for b in noms[i + 1:]:
            if b in vus:
                continue
            if _ecart(heros[a]["empreinte"], heros[b]["empreinte"]) <= SEUIL_VARIANTE:
                groupe.append(b)
        if len(groupe) > 1:
            vus.update(groupe)
            # Deux traductions d'un meme article partagent legitimement la photo.
            fichiers = {n.rsplit("/", 1)[-1] for n in groupe}
            traductions = all(
                fichiers - {n.rsplit("/", 1)[-1]} <= heros[n]["alternates"] for n in groupe)
            if not traductions:
                groupes.append(groupe)
                moyen.append("Meme photo sur des articles qui ne sont pas traductions "
                             "l'un de l'autre : " + ", ".join(f"`{n}`" for n in groupe))

    return [f"- {len(familles)} familles d'images sur {len(LANGS)} langues, "
            f"{len(utilisees)} affichees, {len(reserve)} en reserve",
            f"- {ecarts} variante(s) desynchronisee(s), {len(empruntes)} photo(s) empruntee(s) "
            f"a la reserve, {len(groupes)} groupe(s) d'articles differents illustres pareil"]


# ------------------------------------------------------- I. ancres internes
def section_i():
    """Ancres internes, ajoutee le 04/09/2026.

    `en/best-free-pos-system-2026.html` avait au sommaire une entree « The 2026
    ranking » qui pointait sur #ranking, alors qu'aucun element de la page ne
    portait cet identifiant : le titre avait saute a la traduction. On cliquait,
    rien ne bougeait. Aucune section ne pouvait l'attraper : la C verifie que les
    fichiers cibles existent, pas que les ancres tombent quelque part.

    On controle aussi les identifiants en double, qui cassent la meme chose d'une
    autre facon : le navigateur ne saute que sur le premier.
    """
    casses = doubles = 0
    for lg, d in LANGS.items():
        for p in pages(d):
            nom = p.relative_to(ROOT)
            s = p.read_text(encoding="utf-8")
            vus, deja = set(), set()
            for i in re.findall(r'\sid="([^"]+)"', s):
                if i in vus and i not in deja:
                    moyen.append(f"`{nom}` : l'identifiant `#{i}` est utilise deux fois")
                    deja.add(i)
                    doubles += 1
                vus.add(i)
            for a in dict.fromkeys(re.findall(r'href="#([^"]+)"', s)):
                if a not in vus:
                    moyen.append(f"`{nom}` : le lien `#{a}` du sommaire ne mene nulle part")
                    casses += 1
    return [f"- {casses} ancre(s) cassee(s), {doubles} identifiant(s) en double"]


# ----------------------------------------------------------------- J. hreflang
def _url_de(lg, p):
    """URL publique d'une page, telle qu'elle doit apparaitre en hreflang."""
    prefixe = "" if lg == "fr" else f"{lg}/"
    return BASE + "/" + prefixe + ("" if p.name == "index.html" else p.name)


def section_j():
    """Reciprocite hreflang, ajoutee le 04/09/2026.

    Le site vit en cinq langues. Google n'accepte une grappe de traductions que
    si elle est complete : chaque page doit se declarer elle-meme et declarer ses
    soeurs, et chaque soeur doit lui repondre. Une declaration a sens unique est
    ignoree en silence, et les deux pages se retrouvent a se cannibaliser dans
    les resultats. Rien ne se voit a l'oeil, d'ou ce controle.
    """
    declare, connues = {}, {}
    for lg, d in LANGS.items():
        for p in pages(d):
            u = _url_de(lg, p).rstrip("/") or BASE
            connues[u] = p.relative_to(ROOT).as_posix()
    for lg, d in LANGS.items():
        for p in pages(d):
            s = p.read_text(encoding="utf-8")
            liens = {}
            for balise in re.findall(r'<link[^>]*rel="alternate"[^>]*>', s):
                h = re.search(r'hreflang="([^"]+)"', balise)
                href = re.search(r'href="([^"]+)"', balise)
                if h and href:
                    liens[h.group(1)] = href.group(1).rstrip("/") or BASE
            declare[p.relative_to(ROOT).as_posix()] = (_url_de(lg, p).rstrip("/") or BASE, liens)

    ecarts = 0
    for nom, (moi, liens) in sorted(declare.items()):
        if not liens:
            continue
        if moi not in liens.values():
            moyen.append(f"`{nom}` : grappe hreflang sans auto-reference")
            ecarts += 1
        for code, u in sorted(liens.items()):
            if code == "x-default":
                continue
            cible = connues.get(u)
            if cible is None:
                moyen.append(f"`{nom}` : hreflang `{code}` vers une page qui n'existe pas, {u}")
                ecarts += 1
                continue
            if cible == nom:
                continue
            if moi not in declare.get(cible, (None, {}))[1].values():
                moyen.append(f"`{nom}` declare `{cible}` en hreflang, qui ne le declare pas en retour")
                ecarts += 1
    return [f"- {len(declare)} pages, {ecarts} ecart(s) hreflang"]


# --------------------------------------------------------- K. liens de sources
# Domaines qui refusent les robots (403 systematique) mais repondent normalement
# dans un navigateur. Les compter comme casses ferait crier le rapport pour rien.
ANTI_ROBOT = ("trustpilot.com", "capterra.com", "reclameaqui.com.br", "portaldaqueixa.com",
              "help.loyverse.com", "reclamos.cl", "bportugal.pt", "gob.mx", "une.cd",
              "linkedin.com", "facebook.com", "instagram.com")
JOURS_ENTRE_DEUX_PASSAGES = 7
NAVIGATEUR = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126 Safari/537.36")


def _memes_cibles(a, b):
    """Deux URLs designent-elles la meme page ? Tolere le www, le / final et les
    segments de langue ajoutes par redirection (help.sumup.com -> /en-GB)."""
    if re.fullmatch(r"https?://[^/]+/?", a):
        return True               # une racine qui part sur /accueil ou /home, c'est normal

    def net(u):
        u = re.sub(r"^https?://", "", u).split("?")[0].replace("www.", "").rstrip("/")
        bouts = u.split("/")
        while len(bouts) > 1 and re.fullmatch(r"[a-z]{2}(-[a-zA-Z]{2})?", bouts[-1]):
            bouts.pop()
        return "/".join(bouts)
    return net(a) == net(b)


def _tester_lien(url):
    """(url, code, url finale). Code 0 si la requete n'aboutit pas.

    GET et pas HEAD, malgre le cout : au premier passage, gob.mx et une.cd
    repondaient 404 a un HEAD et 200 a un GET, et aip.ci redirigeait le HEAD vers
    l'image de l'article. Trois sources vivantes declarees mortes ou deplacees.
    125 liens une fois par semaine, la depense est negligeable.
    """
    req = urllib.request.Request(url, headers={
        "User-Agent": NAVIGATEUR,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",   # le corps n'est jamais lu, seul le code compte
        "Upgrade-Insecure-Requests": "1", "Connection": "close"})
    code, final = 0, ""
    for essai in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return url, r.status, r.geturl()
        except urllib.error.HTTPError as e:
            code = e.code
            if e.code < 500:
                return url, e.code, ""      # un 404 ne guerit pas en insistant
        except Exception:
            code = 0
        if essai == 1:
            time.sleep(2)
    return url, code, final


def section_k(force=False):
    """Sante des liens de sources, ajoutee le 04/09/2026.

    Le site tire son autorite de ses sources officielles. Trois facons de les
    perdre, et une seule se voit avec un verificateur de liens ordinaire :

      1. le lien meurt (404, domaine parti) ;
      2. l'adresse officielle demenage sans redirection utile ;
      3. le pire, le lien repond 200 mais ne dit plus la meme chose. Square a
         reaffecte le numero d'article 3796 : l'URL citee comme source des frais
         par transaction redirigeait vers un article sur la vie privee. Aucun
         code d'erreur, une source qui ment.

    D'ou le controle des redirections en plus des codes d'erreur. Passage
    hebdomadaire : une centaine de requetes sortantes, inutile tous les jours.
    """
    import concurrent.futures
    import json as _json
    memo = ROOT / "automation" / "liens-externes.json"
    aujourdhui = datetime.now(timezone.utc).date()
    if not force and memo.is_file():
        try:
            precedent = _json.loads(memo.read_text(encoding="utf-8")).get("derniere_verification")
            if precedent and (aujourdhui - datetime.strptime(precedent, "%Y-%m-%d").date()).days < JOURS_ENTRE_DEUX_PASSAGES:
                return [f"- Sautee : deja passee le {precedent} (une fois par semaine, "
                        f"`--liens` pour forcer)."]
        except Exception:
            pass

    liens = {}
    for lg, d in LANGS.items():
        for p in pages(d):
            for u in re.findall(r'href="(https?://[^"]+)"', p.read_text(encoding="utf-8")):
                if "mybusinessnotebook.com" in u:
                    continue
                liens.setdefault(u, set()).add(p.relative_to(ROOT).as_posix())

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        resultats = list(ex.map(_tester_lien, sorted(liens)))

    morts = bloques = deplaces = douteux = 0
    for url, code, final in resultats:
        ou = ", ".join(f"`{x}`" for x in sorted(liens[url])[:3])
        anti = any(dom in url for dom in ANTI_ROBOT)
        if code == 200:
            if final and not _memes_cibles(url, final):
                cosmetique.append(f"Source deplacee : {url} arrive sur {final} ({ou})")
                deplaces += 1
        elif anti or code in (401, 403, 429):
            bloques += 1
        elif code in (404, 410):
            moyen.append(f"Source morte (`{code}`) : {url} ({ou})")
            morts += 1
        else:
            cosmetique.append(f"Source sans reponse (`{code or 'silence'}`) au moment du "
                              f"controle, a revoir au prochain passage : {url} ({ou})")
            douteux += 1

    memo.write_text(_json.dumps({"derniere_verification": aujourdhui.strftime("%Y-%m-%d"),
                                 "liens_testes": len(resultats), "morts": morts,
                                 "deplaces": deplaces}, indent=2) + "\n", encoding="utf-8")
    return [f"- {len(resultats)} liens de sources testes, {morts} mort(s), "
            f"{deplaces} deplace(s), {douteux} sans reponse, "
            f"{bloques} non testable(s) (anti-robot)"]


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
    i, j = section_i(), section_j()
    k = (["- Sautee (mode --disk-only)."] if disk_only
         else section_k("--liens" in sys.argv))

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
        f"## I. Ancres internes\n\n" + "\n".join(i) + "\n\n"
        f"## J. Reciprocite hreflang\n\n" + "\n".join(j) + "\n\n"
        f"## K. Liens de sources\n\n" + "\n".join(k) + "\n\n"
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
