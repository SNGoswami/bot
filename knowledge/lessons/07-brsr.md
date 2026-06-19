**BRSR** = professional-role assessments tied to **clients**.

**UI:** `modules/brsr/ui/`
**API:** `/api/brsr` — list, create, get by id
**Backend:** `module/brsr/`
**Table:** `brsr_assessments` (`client_id`, `fiscal_year`, completion %, E/S/G scores)

**Disclosure reports** (workforce, governance, stakeholder HR) hang off the same client:
- Optional `brsr_assessment_id` FK on report tables
- Each has its own KPI engine under `module/{name}/engine/`

**Who uses it:** CA, CS, ESG Consultant, Assurer/Auditor — not MSME directly for BRSR workspace.

**Trace:** `/trace brsr-create`
**Schema:** `/schema brsr_assessments`
