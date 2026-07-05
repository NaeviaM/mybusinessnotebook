// Vercel Edge Middleware, auto-langue selon le pays (IP) du visiteur.
// FR est servi à la racine "/"; EN/ES/PT dans /en /es /pt.
// Override manuel via ?lang=xx (mémorisé en cookie 1 an).
// Pose aussi un cookie mbn_geo=<PAYS> pour le ciblage géo côté page (ex: masquer
// les contenus Afrique aux visiteurs hors Afrique francophone).
import { next } from '@vercel/edge';

export const config = { matcher: '/' };

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

export default function middleware(request) {
  const url = new URL(request.url);
  const override = (url.searchParams.get('lang') || '').toLowerCase();
  const cookie = request.headers.get('cookie') || '';
  const cookieLang = (/(?:^|;\s*)site_lang=([a-z]{2})/.exec(cookie) || [])[1];
  const country = (request.headers.get('x-vercel-ip-country') || '').toUpperCase();
  const geoCookie = 'mbn_geo=' + (country || 'XX') + '; Path=/; Max-Age=86400; SameSite=Lax';

  let lang = override || cookieLang || LANG_BY_COUNTRY[country] || 'en';
  if (!['fr', 'en', 'es', 'pt'].includes(lang)) lang = 'en';

  const dest = lang === 'fr' ? '/' : '/' + lang + '/';

  // Déjà au bon endroit (racine FR), aucun override : on sert la page en posant le cookie géo.
  if (dest === '/' && !override) {
    return next({ headers: { 'Set-Cookie': geoCookie } });
  }

  const headers = new Headers({ Location: dest });
  headers.append('Set-Cookie', geoCookie);
  if (override) {
    headers.append('Set-Cookie', 'site_lang=' + lang + '; Path=/; Max-Age=31536000; SameSite=Lax');
  }
  return new Response(null, { status: 307, headers });
}
