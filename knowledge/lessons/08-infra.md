**Runtime:**
| Service | Hosting / notes |
|---------|-----------------|
| Next.js UI | Vercel or local `:3000` |
| Spring API | Elastic Beanstalk (`saathi/Procfile` → JAR) |
| PostgreSQL | Supabase pooler |
| Redis | Local dev / Railway prod — JWT blacklist, rate limits |
| Gemini | Lighthouse + AI Advisor |
| Sanity | Blog CMS |
| Discord | Health webhook (`DiscordWebhookClient`) |

**Env vars (names only — never commit values):**
- `DISCORD_TOKEN` — this bot
- `DISCORD_WEBHOOK_URL` — ops health reports
- `NEXT_PUBLIC_API_URL` — UI → Spring
- DB / Redis / Gemini keys in Spring `application.yaml` or secrets manager

**Health monitoring:** `HealthReportScheduler` posts hourly embeds (DB, Redis, API traffic, signups).

**Future:** `microservices-saathi-api` splits identity, lighthouse, billing, gateway — monolith is live path today.
