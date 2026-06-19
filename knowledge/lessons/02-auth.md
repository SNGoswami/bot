**Session model:** Stateless JWT in an **HttpOnly cookie** (not localStorage).

| Layer | Location | Role |
|-------|----------|------|
| Cookie set | Spring `CookieUtil` | `__Host-sid` (prod) or `token` (local HTTP) |
| Filter | `JwtAuthFilter` | Bearer header or cookie → SecurityContext |
| Blacklist | Redis | Logout / revoked JTIs |
| User cache | Redis | ~5 min TTL |
| Edge guard | `esg-saathi-ui/proxy.ts` | Blocks `/user/*` without valid JWT |
| Client session | `AuthContext.tsx` | `/api/auth/me` + proactive refresh |

**Lifecycle:**
1. Login / verify-otp → Spring sets cookie
2. Every API call → `fetchWithSession` with `credentials: "include"`
3. 401 → `POST /api/auth/refresh` once → retry
4. Still 401 → redirect `/login?reauth=1`
5. Logout → blacklist JTI + clear cookie

**Roles:** `MSME`, `CA`, `CS`, `ESG_CONSULTANT`, `ASSURER_AUDITOR`, `ADMIN`

Dashboard nav RBAC: `modules/dashboard/nav/dashboardNav.ts`

**Trace it:** `/trace login-otp`
