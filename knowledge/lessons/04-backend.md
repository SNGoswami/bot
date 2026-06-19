Backend code: **`saathi/src/main/java/com/esg/saathi/`**

```
module/
├── auth/           Users, JWT, OTP, SecurityConfig
├── profile/        Role profiles (MSME, CA, CS, …)
├── client/         Professional client portfolio
├── lighthouse/     Assessment + Gemini scoring
├── brsr/           BRSR assessments
├── scope3/         Scope 3 calculators
├── workforce/      Workforce KPI reports
├── governance/     Governance reports
├── stakeholderhr/  Stakeholder HR reports
├── aiadvisor/      AI chat + quota
└── contact/        Waitlist / contact entities

common/
└── monitoring/     Discord health webhook
```

**Per-module pattern:**
`controller/` → `service/` → `repository/` → `entity/`

Controllers stay thin; business logic in services. Modules should not call each other's repositories directly.

**Lookup:** `/where brsr` or `/api /api/brsr`
