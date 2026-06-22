# Step 13 — Deploy NEXTGIC AI OPS CENTER

Deploy **backend first**, then **frontend** (frontend needs the Railway URL).

---

## Part A — Backend on Railway (~10 min)

### 1. Push backend to GitHub

```powershell
cd "e:\n8n_data\nextgic-agent (1)"
git init
git add .
git commit -m "Add dashboard API, JWT auth, and Railway deploy config"
# Create empty repo on GitHub: nextgic-agent — then:
git remote add origin https://github.com/YOUR_USER/nextgic-agent.git
git branch -M main
git push -u origin main
```

### 2. Create Railway project

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Select **nextgic-agent**
3. Railway auto-detects Python via `requirements.txt` + `Procfile` / `railway.toml`

### 3. Railway variables (Settings → Variables)

| Variable | Value |
|----------|--------|
| `JWT_SECRET` | Run: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `CORS_ORIGINS` | `https://YOUR-NETLIFY-SITE.netlify.app` (update after Part B) |
| `DASHBOARD_ADMIN_EMAIL` | Your admin email |
| `DASHBOARD_ADMIN_PASSWORD` | Strong password |
| `AGENT_API_KEY` | Your existing agent key |
| `WC_URL`, `WC_CONSUMER_KEY`, `WC_CONSUMER_SECRET` | From your `.env` |
| `NVIDIA_API_KEY` or `OPENAI_API_KEY` | From your `.env` |

Optional: add **PostgreSQL** plugin in Railway → copy `DATABASE_URL` → set as variable (overrides SQLite).

### 4. Get public URL

Settings → **Networking** → **Generate Domain**  
Example: `https://nextgic-agent-production.up.railway.app`

### 5. Verify

```powershell
curl https://YOUR-RAILWAY-URL.up.railway.app/health
curl https://YOUR-RAILWAY-URL.up.railway.app/api/kpis
```

---

## Part B — Frontend on Netlify (~10 min)

### 1. Push frontend to GitHub

```powershell
cd "e:\n8n_data\Cursor\dashboard"
git init
git add .
git commit -m "NEXTGIC AI Ops Center dashboard"
git remote add origin https://github.com/YOUR_USER/nextgic-dashboard.git
git branch -M main
git push -u origin main
```

### 2. Create Netlify site

1. [app.netlify.com](https://app.netlify.com) → **Add new site** → **Import from Git**
2. Select **nextgic-dashboard**
3. Build settings (auto from `netlify.toml`):
   - Build command: `npm run build`
   - Plugin: `@netlify/plugin-nextjs`

### 3. Netlify environment variables

| Variable | Value |
|----------|--------|
| `NEXT_PUBLIC_API_URL` | `https://YOUR-RAILWAY-URL.up.railway.app` |
| `NEXT_PUBLIC_WS_URL` | `wss://YOUR-RAILWAY-URL.up.railway.app` |

**Deploy site** → note URL, e.g. `https://nextgic-dashboard.netlify.app`

### 4. Update Railway CORS

Back in Railway → Variables:

```
CORS_ORIGINS=https://nextgic-dashboard.netlify.app
```

Redeploy backend (or wait for auto-redeploy).

### 5. Login

Open Netlify URL → sign in with `DASHBOARD_ADMIN_EMAIL` / `DASHBOARD_ADMIN_PASSWORD`.

---

## Optional — CLI deploy (no global install)

```powershell
# Backend
cd "e:\n8n_data\nextgic-agent (1)"
npx @railway/cli login
npx @railway/cli init
npx @railway/cli up

# Frontend
cd "e:\n8n_data\Cursor\dashboard"
npx netlify-cli login
npx netlify-cli init
npx netlify-cli deploy --prod
```

Set env vars in each platform’s dashboard after first deploy.

---

## Checklist after deploy

- [ ] `curl https://RAILWAY/health` → `{"status":"ok"}`
- [ ] Netlify site loads `/login`
- [ ] Login works (JWT)
- [ ] `/dashboard` shows real KPIs
- [ ] `/live` shows tasks; WebSocket shows **LIVE**
- [ ] Mobile: sidebar collapses

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| CORS errors in browser | Add exact Netlify URL to `CORS_ORIGINS` on Railway |
| WebSocket disconnected | Use `wss://` not `ws://` in `NEXT_PUBLIC_WS_URL` |
| Login 401 | Redeploy Railway after first boot (admin user created on startup) |
| Empty KPIs | Backend DB empty on new deploy — run agents or copy SQLite |
