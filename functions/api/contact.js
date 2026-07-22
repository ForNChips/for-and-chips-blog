/**
 * Contact-form endpoint — Cloudflare Pages Function (POST /api/contact).
 *
 * Receives the /about/ form, forwards it by email via the Resend API, and
 * redirects back to /about/ with a status flag the page renders as a banner:
 *   ?sent=1                    → success
 *   ?sent=0&reason=missing     → a required field was empty
 *   ?sent=0&reason=invalid     → email failed the sanity check
 *   ?sent=0&reason=unconfigured→ env vars not set on this deployment (demo)
 *   ?sent=0&reason=send        → Resend rejected the request
 *
 * Environment variables (Pages project → Settings → Environment variables):
 *   RESEND_API_KEY     secret — Resend API key
 *   CONTACT_TO_EMAIL   where submissions land (e.g. contact@forandchips.com)
 *   CONTACT_FROM_EMAIL verified Resend sender (e.g. contact-form@forandchips.com)
 *
 * Spam handling: the form carries a hidden `_gotcha` honeypot; bots that fill
 * it get a fake success so they don't retry.
 */

const LIMITS = { name: 200, email: 320, message: 10000 };

export async function onRequestPost({ request, env }) {
  const back = (params) =>
    Response.redirect(new URL(`/about/${params}#contact-status`, request.url).toString(), 303);

  let form;
  try {
    form = await request.formData();
  } catch {
    return back('?sent=0&reason=invalid');
  }

  const field = (k) => (form.get(k) || '').toString().trim().slice(0, LIMITS[k] || 1000);
  const name = field('name');
  const email = field('email');
  const message = field('message');

  if ((form.get('_gotcha') || '').toString().trim() !== '') return back('?sent=1');
  if (!name || !email || !message) return back('?sent=0&reason=missing');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return back('?sent=0&reason=invalid');
  if (!env.RESEND_API_KEY || !env.CONTACT_TO_EMAIL) return back('?sent=0&reason=unconfigured');

  const body = {
    from: env.CONTACT_FROM_EMAIL || 'contact-form@forandchips.com',
    to: [env.CONTACT_TO_EMAIL],
    reply_to: email,
    subject: `[For&Chips] Message from ${name}`,
    text: `${message}\n\n—\nFrom: ${name} <${email}>\nPage: ${request.headers.get('referer') || 'unknown'}`,
  };

  let resp;
  try {
    resp = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
  } catch {
    return back('?sent=0&reason=send');
  }

  return back(resp.ok ? '?sent=1' : '?sent=0&reason=send');
}
