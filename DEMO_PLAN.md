# Week 1 Demo Plan — Azure Serverless

> **Time:** ~15–20 minutes  
> **Tools open:** VS Code, browser (index.html), Postman, Azure Portal  
> **Start with:** `func start` running in terminal, browser open on index.html

---

## Opening (1 min) — Set the context

> *Say this to your mentor:*

"This week I worked on setting up a Python-based Azure serverless environment and building my first Azure Functions. I'll walk you through each task I completed — starting with local setup, then the APIs I built, then Key Vault integration, and finally the deployment.

I also built a small frontend learning lab to practice connecting everything together."

---

## Task 1 — Environment Setup (2 min)

**What to show:** Open VS Code terminal, run these one by one:

```bash
python --version          # 3.11.x
func --version            # 4.x.x  (Azure Functions Core Tools)
az --version              # Azure CLI
```

**What to say:**
- "I installed Python 3.11 — Azure Functions requires this specific version for the Python worker."
- "Azure Functions Core Tools (`func`) lets me run functions locally before deploying — so I can test everything without pushing to Azure."
- "I set up a virtual environment with `.venv` and all dependencies are in `requirements.txt` — including `azure-functions`, `azure-identity`, `azure-keyvault-secrets`, and `azure-storage-blob`."
- "I created a GitHub repo to track everything."

**What to click:** Show `requirements.txt` in VS Code. Show `.venv` folder in the Explorer.

---

## Task 2 — Health Check API (3 min)

**What to show:** The Health Check section in index.html (or Postman)

**Step 1:** Show the code in `function_app.py` — the `health` function:
```
GET /api/health
→ { "status": "running", "timestamp": "..." }
```

**Step 2:** In browser (index.html) → click **"GET /api/health"** button  
*OR* In Postman → `GET http://localhost:7071/api/health`

**What to say:**
- "This is the first API I built — a health check endpoint. In real production systems, monitoring tools like Azure Monitor ping this every minute to confirm the service is alive."
- "The route decorator `@app.route(route='health', methods=['GET'])` — that's how Azure Functions maps a URL to a Python function. No server config needed."
- "I added a timestamp to the response so you can see it's returning a live value, not a cached one."

---

## Task 3 — Calculator Azure Function (4 min)

**What to show:** The Calculator section in index.html (or Postman)

**Step 1:** Show the code — the `calculate` function in `function_app.py`

**Step 2 (happy path):** In index.html → enter x=10, y=20 → click **"GET /api/calculate"**
```
→ { "x": 10.0, "y": 20.0, "sum": 30.0 }
```

**Step 3 (error path):** Click **"Send Bad Input (error demo)"**
```
→ { "error": "x and y must be numbers", "detail": "..." }
→ HTTP 400
```

**What to say:**
- "Azure Functions reads query parameters from `req.params.get('x')` — it's simple but powerful."
- "I learned about function bindings — the `@app.route` decorator is the input binding that maps HTTP requests to this function."
- "I also added error handling using try/except. If someone sends letters instead of numbers, the function catches the `ValueError`, logs it with `logging.exception()`, and returns a proper 400 error instead of crashing with a 500."
- "That `logging.exception()` call is important — in Azure, those logs automatically flow to Application Insights, so I can search them later."

**What to show in terminal:** Point to the `func start` output — show the log line printed for each request.

---

## Task 4 — Key Vault Integration (3 min)

**What to show:** Key Vault section in index.html + the code

**Show the code:**
```python
# In function_app.py — /api/secret route
credential = DefaultAzureCredential()
client = SecretClient(vault_url=vault_url, credential=credential)
secret = client.get_secret(secret_name)
```

**What to say:**
- "The most important thing I learned this week: never hardcode API keys or connection strings in code."
- "I stored secrets like the OpenAI API key and database connection string inside Azure Key Vault."
- "The function retrieves them at runtime using `DefaultAzureCredential` — which automatically uses Managed Identity when running in Azure, and my local Azure CLI login when running locally. Zero credentials in the code."
- "I also enabled System Assigned Managed Identity on the Function App and granted it `Get` permission on Key Vault — so the function can read secrets without any passwords."
- "Notice I mask the secret before returning it to the frontend — `secret.value[:3] + '••••'` — the browser never sees the real value."

**What to show in Azure Portal (if deployed):**
- Key Vault → Secrets → show the list of secrets (names visible, values hidden)
- Function App → Identity → show Managed Identity is ON

---

## Task 5 — Deploy to Azure (3 min)

**What to show:** The deployed Azure Function App in Azure Portal

**Walk through:**
1. Open Azure Portal → Function App → your app
2. Click **Functions** → show the list of deployed functions (health, calculate, hello, secret)
3. Click **health** → click **Get Function URL** → paste it in Postman or the index.html base URL bar → show it returns `{"status":"running"}`

**What to say:**
- "Deployment was done with one command: `func azure functionapp publish <app-name>`"
- "The Function App runs on a Consumption plan — I only pay when a function is actually invoked, not for idle time. For learning, it's practically free."
- "After deploying, I validated each endpoint using Postman to confirm they work the same in Azure as they did locally."

**What to show:**
- In index.html → paste the deployed base URL in the top bar → click Health Check → see it return live data from Azure

---

## The Frontend Learning Lab (2 min)

**What to show:** Scroll through index.html

**What to say:**
- "To consolidate everything I learned, I built this frontend learning lab. Each section has two parts — the live UI on the left where I can call my real Azure endpoints, and a backend blueprint on the right with the exact code and steps."
- "This helped me understand the full picture — not just writing the function, but understanding how a frontend actually consumes an API."
- "It also covers the services I'll be working on going forward — Blob Storage triggers, Timer triggers for scheduled jobs, and Application Insights for monitoring."

---

## Wrap-up — What I Learned (1 min)

> *Say this to close:*

"The biggest things I took away from this week:

1. **Azure Functions are just Python functions** — the decorator handles all the HTTP routing and Azure wiring.
2. **Never hardcode credentials** — Key Vault + Managed Identity is the right pattern, and it's actually simpler once you understand it.
3. **Local development with `func start` is fast** — I could iterate without deploying every time.
4. **Error handling matters from day one** — the difference between a 500 crash and a meaningful 400 response is just a try/except and a logging call.

Next I want to dive deeper into Blob triggers and Application Insights monitoring."

---

## Quick Cheat Sheet — URLs to have ready

| Endpoint | Local | Azure |
|---|---|---|
| Health | `http://localhost:7071/api/health` | `https://<app>.azurewebsites.net/api/health` |
| Calculator | `http://localhost:7071/api/calculate?x=10&y=20` | `https://<app>.azurewebsites.net/api/calculate?x=10&y=20` |
| Hello | `http://localhost:7071/api/hello` (POST) | `https://<app>.azurewebsites.net/api/hello` |
| Secret | `http://localhost:7071/api/secret` (POST) | `https://<app>.azurewebsites.net/api/secret` |

---

## If Something Goes Wrong

| Problem | Quick fix |
|---|---|
| `func start` fails | Check `.venv` is activated: `.\.venv\Scripts\activate` |
| 401 Unauthorized | Function App auth level is ANONYMOUS — check `local.settings.json` |
| CORS error in browser | Add `*` to Function App → CORS settings in Azure Portal |
| Key Vault 403 | Managed Identity needs `Get` permission in Key Vault Access Policies |
| Import errors | Run `.\.venv\Scripts\pip install -r requirements.txt` |
