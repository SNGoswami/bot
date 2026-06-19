**ESG Saathi** spans several repositories under `ESG-Saathi/`:

| Repo | Role | Default port |
|------|------|--------------|
| `esg-saathi-ui` | Next.js frontend + BFF routes | 3000 |
| `saathi` | Main Spring Boot API (production monolith) | 8080 |
| `saathi-fast-api` | Python FastAPI utilities (PDF extract) | varies |
| `microservices-saathi-api` | Target microservice split (future) | gateway |
| `bot` | This Discord mentor | — |

**Request path (happy path):**
Browser → Next.js (`credentials: include`) → Spring `/api/*` → PostgreSQL + Redis.

**Side integrations:**
- Supabase — contact/waitlist via Next.js BFF (`app/api/database/*`)
- Sanity — blog content (read from UI)
- Gemini — Lighthouse scoring + AI Advisor
- Discord webhook — hourly health reports from Spring

Canonical docs: `esg-saathi-ui/docs/ARCHITECTURE.md` and `API_ARCHITECTURE.md`.

**Next:** `/learn next` or `/topic auth`
