#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controle de sante quotidien de My Business Notebook.

Remplace l'agent cloud "daily health check", tombe en panne le 04/08/2026.
Aucun modele de langage n'est necessaire : tous les controles sont deterministes.
Avantage sur l'ancien agent : GitHub Actions a un vrai acces reseau sortant, donc
la verification EN DIRECT est enfin possible (le bac a sable cloud la bloquait).

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
LANGS = {"fr": ROOT, "en": ROOT / "en", "es": ROOT / "es", "pt": ROOT / "pt"}
SKIP = {"google5f267a48e7657a47.html"}

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
def section_a():
    lignes = []
    for label, url in [("apex", BASE + "/"), ("www", "https://www.mybusinessnotebook.com/"),
                       ("secours Vercel", FALLBACK + "/"),
                       ("accueil EN", BASE + "/en/"), ("accueil ES", BASE + "/es/"),
                       ("accueil PT", BASE + "/pt/")]:
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
                if not (d / t).exists():
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


def main():
    maintenant = datetime.now(timezone.utc)
    a = section_a()
    b, _ = section_b()
    c, d, e, f = section_c(), section_d(), section_e(), section_f()

    statut = "CRITIQUE" if critique else ("DEGRADE" if moyen else "OK")

    def bloc(titre, items):
        if not items:
            return f"## {titre}\n\nAucun probleme trouve.\n"
        return f"## {titre}\n\n" + "\n".join(f"- {x}" for x in items[:40]) + \
               (f"\n- ... et {len(items)-40} autre(s)\n" if len(items) > 40 else "\n")

    rapport = (
        f"# Rapport de sante, {maintenant:%Y-%m-%d %H:%M} UTC\n\n"
        f"VERIF LIVE : EFFECTUEE\n\n"
        f"**STATUT GLOBAL : {statut}**\n\n"
        f"Genere par GitHub Actions (`.github/workflows/health-check.yml`), "
        f"sans modele de langage. Remplace l'agent cloud tombe en panne le 04/08/2026.\n\n"
        f"## A. Disponibilite en direct\n\n" + "\n".join(a) + "\n\n"
        f"## B. Balayage du sitemap en direct\n\n" + "\n".join(b) + "\n\n"
        f"## C. Liens et images sur disque\n\n" + "\n".join(c) + "\n\n"
        f"## D. Coherence du sitemap\n\n" + "\n".join(d) + "\n\n"
        f"## E. Balises d'en-tete\n\n" + "\n".join(e) + "\n\n"
        f"## F. Cosmetique\n\n" + "\n".join(f) + "\n\n"
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
