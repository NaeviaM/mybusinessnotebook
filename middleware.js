// Vercel Edge Middleware.
// - AUCUNE redirection automatique par pays. Elle a existé jusqu'au 31/08/2026,
//   avec une liste d'agents pour en exempter les robots. C'était du cloaking au
//   sens littéral des règles anti-spam de Google : un visiteur américain sur "/"
//   partait en 307 vers /en/, Googlebot recevait la même URL en 200. Et l'agent
//   Google-InspectionTool, qui ne contient ni "bot" ni "crawler" dans son nom,
//   tombait du mauvais côté du test : le test en direct de la Search Console ne
//   voyait donc pas ce que voit l'index. La bonne pratique documentée par Google
//   pour un site multilingue est hreflang + un bandeau côté client, pas une
//   redirection : c'est ce que font désormais les accueils, via /geo.
// - FR est servi à la racine "/"; EN/ES/PT dans /en /es /pt.
// - Bouton de langue : ?lang=xx fonctionne DÉSORMAIS sur TOUTES les pages
//   (accueil, /index.html, /en//es//pt/, et les articles), mémorisé en cookie 1 an.
//   La plupart des articles n'existent que dans une langue : changer de langue
//   depuis un article renvoie donc vers l'accueil de la langue choisie.

export const config = {
  // On exécute le middleware sur les PAGES, jamais sur les fichiers statiques
  // (images, css, js, xml, txt…) — sinon on gaspille des invocations et on
  // risquerait de rediriger un asset. NB : les .html RESTENT couverts.
  matcher: '/((?!.*\\.(?:css|js|mjs|png|jpe?g|webp|gif|svg|ico|xml|txt|json|webmanifest|woff2?|map)).*)',
};

const LANGS = ['fr', 'en', 'es', 'pt'];
const home = (lang) => (lang === 'fr' ? '/' : '/' + lang + '/');

export default function middleware(request) {
  const url0 = new URL(request.url);

  // 0) Un seul hôte indexable. L'hôte de secours Vercel servait encore en 200
  //    les cinq accueils (les chemins sans extension échappent à la règle de
  //    redirection de vercel.json, car ils passent d'abord par ce middleware),
  //    et son robots.txt, lui, était redirigé, donc illisible.
  if (url0.hostname !== 'mybusinessnotebook.com') {
    url0.hostname = 'mybusinessnotebook.com';
    return Response.redirect(url0.toString(), 308);
  }

  // 0 bis) Point d'accès qui renvoie le pays du visiteur, déduit de son adresse
  //    IP par Vercel. La page d'accueil l'interroge en JavaScript pour remonter
  //    les articles qui concernent ce pays et repousser ceux d'un autre pays.
  //
  //    Pourquoi un appel séparé plutôt qu'un cookie posé ici : poser un cookie
  //    depuis le middleware oblige à rediriger, et sur l'accueil français, qui
  //    est déjà servi à la racine, cette redirection pointerait vers elle-même,
  //    donc boucle infinie dès que le navigateur refuse le cookie. Un point
  //    d'accès en lecture seule ne peut rien casser.
  //
  //    Les robots ne lisent pas ce point d'accès et ne jouent pas le script :
  //    ils reçoivent la page dans son ordre par défaut, avec TOUS les liens.
  //    Rien n'est masqué à l'indexation, contrairement à l'ancien mécanisme.
  // On accepte les deux écritures : vercel.json ajoute « .html » à toute URL
  // sans extension, et cette règle exclut désormais /geo, mais on garde la
  // variante par sécurité si la configuration change.
  if (url0.pathname === '/geo' || url0.pathname === '/geo.html') {
    const c = (request.headers.get('x-vercel-ip-country') || '').toUpperCase();
    return new Response(JSON.stringify({ country: /^[A-Z]{2}$/.test(c) ? c : null }), {
      headers: {
        'content-type': 'application/json; charset=utf-8',
        'cache-control': 'no-store',
      },
    });
  }

  const url = url0;
  const path = url.pathname;
  const override = (url.searchParams.get('lang') || '').toLowerCase();

  // 1) Choix MANUEL via le bouton de langue : valable PARTOUT.
  //    On mémorise le choix en cookie et on envoie vers l'accueil de la langue.
  if (LANGS.includes(override)) {
    return new Response(null, {
      status: 307,
      headers: {
        Location: home(override),
        'Set-Cookie': 'site_lang=' + override + '; Path=/; Max-Age=31536000; SameSite=Lax',
      },
    });
  }

  // 2) Sans choix manuel, on ne redirige plus personne. L'accueil de chaque
  //    langue reste à son URL, le hreflang dit à Google qu'elles sont
  //    équivalentes, et l'accueil propose lui-même la bonne langue dans un
  //    bandeau discret alimenté par /geo. Même URL, même réponse, pour tout le
  //    monde : c'est la seule façon de rester hors du cloaking.
  return;
}
