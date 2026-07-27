# Deployment — Cloudflare Pages

The site deploys as static output (`hugo --minify`) to Cloudflare Pages.
Environments are driven by Hugo's config overlays:

| Environment | Build command | Config merged | Robots |
|---|---|---|---|
| production | `hugo --minify && npx pagefind@1 --site public` | `config/_default` + `config/production` | index, follow + sitemap |
| demo | `hugo --minify --environment demo && npx pagefind@1 --site public` | `config/_default` + `config/demo` | noindex meta + `Disallow: /` |
| development | `hugo server -D` | `config/_default` | noindex meta |

The `pagefind` step builds the full-text search index (`public/pagefind/`)
from the rendered article pages (`data-pagefind-body` in
`layouts/article/single.html`). The navbar search uses it when present and
falls back to Fuse over `/index.json` (titles + summaries) under
`hugo server`, where the index doesn't exist. Locally, `uvx pagefind --site
<outdir>` runs it without node.

`layouts/robots.txt` emits `Disallow: /` for every non-production environment,
and PaperMod adds `<meta name="robots" content="noindex, nofollow">` whenever
`params.env != "production"`.

## Cloudflare Pages setup (per project)

Create **two Pages projects** from the same GitHub repo:

### 1. `forandchips` (production)
- Production branch: `main`
- Build command: `hugo --minify && npx pagefind@1 --site public`
- Build output directory: `public`
- Environment variables:
  - `HUGO_VERSION` = `0.161.0` (keep in sync with local; Extended is default on Pages)
- Custom domain: `forandchips.com`

### 2. `forandchips-demo`
- Production branch: `demo`
- Build command: `hugo --minify --environment demo && npx pagefind@1 --site public`
- Build output directory: `public`
- Environment variables: `HUGO_VERSION` = `0.161.0`
- Custom domain: `demo.forandchips.com`

Notes:
- The theme is a git submodule — Pages clones submodules automatically, but if
  the build fails with "theme not found", add `git submodule update --init
  --recursive &&` in front of the build command.
- `static/_headers` and `static/_redirects` are picked up by Pages as-is.
- There is deliberately **no `wrangler.toml`**: two Pages projects are built
  from this one repo, and that file's `name` field pins a single project name.
  All build settings live in the dashboard instead. `functions/`,
  `static/_headers` and `static/_redirects` are auto-detected by Pages.

## Third-party services

### Contact form (Cloudflare Pages Function + Resend)

The /about/ form POSTs to `/api/contact`, served by
`functions/api/contact.js` — Pages deploys anything under `functions/`
automatically, no extra build step. The function emails the submission via
[Resend](https://resend.com) and redirects back with a status banner.

Setup (production project only):
1. Create a Resend account, add `forandchips.com` as a domain and set the
   DNS records it asks for (they're one click away in the same Cloudflare
   dashboard). Create an API key.
2. Pages project → Settings → Environment variables (Production):
   - `RESEND_API_KEY` — the API key (mark as secret)
   - `CONTACT_TO_EMAIL` — where submissions land, e.g. `contact@forandchips.com`
   - `CONTACT_FROM_EMAIL` — a sender on the verified domain, e.g. `contact-form@forandchips.com`
3. Nothing to configure on the demo project: without the env vars the
   function redirects back with "form not active on this deployment".

Spam: hidden `_gotcha` honeypot (bots get a fake success). If spam ever
becomes a problem, add Cloudflare Turnstile — it integrates natively with
Pages Functions.

Local note: `hugo server` doesn't run Pages Functions; submitting locally
404s. Test the full loop on a Pages preview deployment, or with
`npx wrangler pages dev` on a machine with node. To hide the form entirely,
set `params.contact.formEndpoint: ""`.

### Donations (Buy Me a Coffee)
In `config/_default/hugo.yaml`:
```yaml
donation:
  enabled: true
  provider: "buymeacoffee"      # or "ko-fi"
  url: "https://buymeacoffee.com/<username>"
  label: "Buy us a coffee"
```

### Analytics (GoatCounter)
1. Create a site at goatcounter.com and note the code (`<code>.goatcounter.com`).
2. Set `params.analytics.goatcounter.code` in `config/_default/hugo.yaml`.
3. It is already `enabled: true` in `config/production/hugo.yaml` only —
   demo and local dev never load the script.
