Product UI code lives under **`esg-saathi-ui/modules/`** — one folder per domain.

| Module | Path | API base |
|--------|------|----------|
| platform | `modules/platform/` | `/api/auth/*` |
| dashboard | `modules/dashboard/` | view registry only |
| lighthouse | `modules/lighthouse/` | `/api/lighthouse/*` |
| brsr | `modules/brsr/` | `/api/brsr/*` |
| clients | `modules/clients/` | `/api/clients/*` |
| scope3-ghg | `modules/scope3-ghg/` | `/api/scope3/*` |
| workforce | `modules/workforce/` | `/api/workforce/*` |
| governance | `modules/governance/` | `/api/governance/*` |
| stakeholder-hr | `modules/stakeholder-hr/` | `/api/stakeholder-hr/*` |
| ai-advisor | `modules/ai-advisor/` | `/api/ai-advisor/*` |
| admin | `modules/admin/` | `/api/admin/*` |

**Rules:**
1. `platform` must not import feature modules
2. All Spring calls go through `modules/platform/api/client.ts` (`apiFetch`)
3. Dashboard views registered in `dashboard/registry/viewRegistry.tsx`
4. `app/` routes are thin — no business logic

**Lookup:** `/where lighthouse` or `/where scope3`
