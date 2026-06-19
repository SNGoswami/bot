**Spine:** `users` → role **profiles** → `clients` → **reports/assessments**

**Core tables:**
- `users` — identity, `role` enum, optional `auth_user_id` (Supabase link)
- `msme_profiles`, `ca_profiles`, `cs_profiles`, `esg_consultant_profiles`, `assurer_auditor_profiles`
- `clients` — owned by `user_id`; one manager profile FK (CA/CS/Consultant/Auditor)
- `lighthouse_assessments` — `msme_profile_id` OR `client_id`
- `brsr_assessments` — per `client_id` + fiscal year
- `workforce_reports`, `governance_reports`, `stakeholder_hr_reports` — `user_id` + `client_id`, optional `brsr_assessment_id`
- `scope3_calculations`, `isf_calculations`, `net_zero_targets`

**Migrations:** `saathi/src/main/resources/db/*.sql` (run manually; Hibernate `ddl-auto: validate`).

**Linkage examples:**
- `/link client brsr`
- `/link client lighthouse`
- `/schema clients`
