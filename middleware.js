// Vercel Edge Middleware.
// - Langue AUTOMATIQUE selon le pays (IP) du visiteur, uniquement sur l'accueil.
//   FR est servi à la racine "/"; EN/ES/PT dans /en /es /pt.
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

const LANG_BY_COUNTRY = {
  // Français (servi à la racine)
  FR:'fr', BE:'fr', CH:'fr', LU:'fr', MC:'fr',
  CI:'fr', SN:'fr', CD:'fr', CG:'fr', CM:'fr', ML:'fr', BF:'fr', NE:'fr', TG:'fr',
  BJ:'fr', GA:'fr', MG:'fr', TD:'fr', GN:'fr', RW:'fr', BI:'fr', DJ:'fr',
  // Español
  ES:'es', MX:'es', AR:'es', CO:'es', CL:'es', PE:'es', VE:'es', EC:'es', GT:'es',
  CU:'es', BO:'es', DO:'es', HN:'es', PY:'es', SV:'es', NI:'es', CR:'es', PA:'es', UY:'es',
  // Português
  BR:'pt', PT:'pt', AO:'pt', MZ:'pt', CV:'pt', GW:'pt',
  // English (par défaut)
  US:'en', GB:'en', AU:'en', NZ:'en', IE:'en', CA:'en', PH:'en', KE:'en', NG:'en',
  GH:'en', ZA:'en', IN:'en', SG:'en', MY:'en', TZ:'en', UG:'en', ZM:'en', ZW:'en'
};

const LANGS = ['fr', 'en', 'es', 'pt'];
const home = (lang) => (lang === 'fr' ? '/' : '/' + lang + '/');

export default function middleware(request) {
  const url = new URL(request.url);
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

  // 2) Sans choix manuel : on n'auto-oriente QUE la page d'accueil.
  //    On ne touche jamais aux articles ni aux accueils de langue (évite de
  //    casser les URLs et toute boucle de redirection).
  if (path !== '/' && path !== '/index.html') return;

  const cookie = request.headers.get('cookie') || '';
  const cookieLang = (/(?:^|;\s*)site_lang=([a-z]{2})/.exec(cookie) || [])[1];
  const country = (request.headers.get('x-vercel-ip-country') || '').toUpperCase();

  let lang = cookieLang || LANG_BY_COUNTRY[country] || 'en';
  if (!LANGS.includes(lang)) lang = 'en';

  if (lang === 'fr') return; // FR est servi à la racine, rien à faire.
  return new Response(null, { status: 307, headers: { Location: home(lang) } });
}
