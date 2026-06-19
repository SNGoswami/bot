**Lighthouse** = MSME ESG readiness assessment with AI scoring.

**UI:** `modules/lighthouse/ui/` — assessment form, list, reports
**API client:** `modules/lighthouse/api/lighthouseApi.ts`
**Endpoints:** `GET /api/lighthouse/me`, `POST /api/lighthouse/submit` (MSME role)
**Backend:** `module/lighthouse/` — `LighthouseAssessmentController`, `LighthouseGeminiService`
**Table:** `lighthouse_assessments`

**Two flows:**
1. **MSME self-serve** — linked via `msme_profile_id`
2. **Advisor flow** — linked via `client_id` (one active assessment per client)

Report includes env / social / gov pillar scores, strengths, improvements.

**Trace:** `/trace lighthouse-submit`
