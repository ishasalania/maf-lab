# Challenge 0 — Environment Setup & Resource Deployment

**Expected Duration: 15 minutes**

---

## What This Challenge Does

Before you can build agents, you need three things working:

1. **A Python environment** with MAF and its dependencies installed
2. **Azure CLI authenticated** so your code can talk to Azure AI Foundry
3. **A `.env` file** with your project endpoint and model name

By the end of this challenge, you'll run a test agent that returns a **structured Pydantic output** — proving your entire stack works end-to-end.

> **If something is not working, raise your hand immediately!** Don't spend more than 5 minutes stuck on setup — that's what coaches are for.

---

## What You Need to Know

| Component | What It Is | Why You Need It |
|-----------|-----------|-----------------|
| **Azure AI Foundry** | Microsoft's platform for hosting AI models | Hosts the GPT-4o model your agents will call |
| **Project Endpoint** | A URL like `https://xxx.services.ai.azure.com/...` | Tells MAF where to send requests |
| **`FoundryChatClient`** | MAF's client class | Connects your Python code to the Foundry endpoint |
| **`AzureCliCredential`** | Auth from `azure-identity` | Uses your `az login` session — no API keys needed |
| **Pydantic** | Python data validation library | Defines the typed output schemas your agents will use |

### How Authentication Works

```
Your Code → AzureCliCredential → az login session → Azure AD → Token → Foundry API
```

No API keys. No secrets in `.env`. Just `az login` and your Azure account does the rest. This is **passwordless authentication** — the recommended pattern for development.

---

## Step 1: Fork & Clone the Repository

Fork this repository to your GitHub account (click **Fork** in the top right), then:

### Option A: GitHub Codespaces (Recommended — Zero Setup)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ishasalania/maf-lab?quickstart=1)

Codespaces gives you:
- Python 3.11 pre-installed
- Azure CLI pre-installed
- All pip packages pre-installed (`agent-framework`, `pydantic`, etc.)
- VS Code in the browser — nothing to install locally

> **This is the fastest path.** Click the button, wait 60 seconds, and you're ready.

### Option B: Local Setup

```bash
git clone https://github.com/<your-username>/maf-lab.git
cd maf-lab
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

Verify Python version:
```bash
python --version
# Should show 3.10 or higher
```

---

## Step 2: Azure CLI Authentication

You need to be logged in to Azure so your code can get tokens:

```bash
az login --use-device-code
```

This gives you a URL and a code. Open the URL in your browser, enter the code, and sign in with your Azure account.

> **Multiple tenants?** Use: `az login --use-device-code --tenant <TENANT_ID>`

Verify it worked:

```bash
az account show --query "{name:name, id:id}" -o table
```

You should see your subscription name and ID.

---

## Step 3: Configure Environment Variables

### If your coach pre-provisioned resources (most likely):

Your coach will provide these values on a slide or handout:

```
FOUNDRY_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project-id
FOUNDRY_MODEL=gpt-4o
```

Create your `.env` file:

```bash
cp .env.example .env
```

Then open `.env` and paste the values your coach gave you.

### If you're deploying your own resources:

Run the deployment script (takes ~3 minutes):

```bash
cd challenge-0/scripts
chmod +x deploy-resources.sh get-keys.sh
./deploy-resources.sh --resource-group maf-workshop --location swedencentral
```

Then retrieve your endpoint:

```bash
./get-keys.sh --resource-group maf-workshop
```

This will:
1. Find your AI Foundry project endpoint
2. Assign **Azure AI Developer** and **Cognitive Services User** roles to your account
3. Auto-populate the `.env` file with the correct values

---

## Step 4: Understand What Was Deployed

Your resource group should contain (your coach may show this on a slide):

| Resource | Type | Purpose |
|----------|------|---------|
| AI Foundry Hub | `Microsoft.CognitiveServices/AIFoundry` | The project that holds everything together |
| AI Services | `Microsoft.CognitiveServices/AIServices` | The inference endpoint for models |
| GPT-4o deployment | Model Deployment (GlobalStandard) | The specific model your agents will call |

That's it — just 2-3 Azure resources. No storage accounts, no databases, no networking setup. MAF is lightweight.

### How the pieces connect:

```
Your .env file:
  FOUNDRY_PROJECT_ENDPOINT = "https://xxx.services.ai.azure.com/api/projects/yyy"
  FOUNDRY_MODEL = "gpt-4o"
         │                            │
         ▼                            ▼
  FoundryChatClient(              model="gpt-4o"
    project_endpoint=...,              │
    credential=AzureCliCredential()    │
  )                                    │
         │                             │
         ▼                             ▼
  Azure AI Foundry Project ──→ GPT-4o Deployment
```

---

## Step 5: Run the Verification Notebook

Open `challenge-0/verify-setup.ipynb` and **run all cells** (Shift+Enter through each one).

You should see:

```
✅ Python 3.11
✅ agent-framework (installed)
✅ azure-identity (installed)
✅ pydantic (installed)
✅ python-dotenv (installed)
✅ MAF core imports working (Agent, WorkflowBuilder, FoundryChatClient)
✅ FOUNDRY_PROJECT_ENDPOINT: https://your-project...
✅ FOUNDRY_MODEL: gpt-4o
✅ Azure CLI authenticated (token acquired)
✅ Agent responded with structured output: {'message': '...', 'ready': True}

🎉 ALL CHECKS PASSED — You're ready for the workshop!
```

### What the test does:

The final cell creates a real agent with a Pydantic output schema:

```python
class TestResponse(BaseModel):
    message: str
    ready: bool

test_agent = Agent(
    client=FoundryChatClient(...),
    name="SetupTestAgent",
    instructions="Always respond with ready=true and a short message.",
    default_options=OpenAIChatOptions[Any](response_format=TestResponse),
)

response = await test_agent.run("Are we ready?")
result = TestResponse.model_validate_json(response.text)
# result.ready == True  ← This proves structured output works!
```

This is the **exact same pattern** you'll use throughout Challenges 1–3. If this cell passes, everything is working.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: agent_framework` | Run `pip install -r requirements.txt` |
| `FOUNDRY_PROJECT_ENDPOINT not set` | Check your `.env` file exists and has the right value |
| `AuthenticationError` | Run `az login --use-device-code` again |
| `Resource not found (404)` | Check the endpoint URL — it should end with `/api/projects/...` |
| `Model not found` | Check `FOUNDRY_MODEL` in `.env` matches your deployment name |
| `Rate limit (429)` | Wait 30 seconds and retry — GPT-4o has per-minute limits |
| Token expired | Run `az account get-access-token` — if it fails, `az login` again |

---

## Success Criteria

- [ ] `az account show` displays your subscription
- [ ] `.env` file exists with `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL`
- [ ] All 5 cells in `verify-setup.ipynb` show ✅
- [ ] The test agent returns `{'message': '...', 'ready': True}` (structured output works!)

---

## ➡️ Next Challenge

Everything works! Time to build real agents.

In **[Challenge 1: Structured Agents](../challenge-1/README.md)**, you'll build 4 specialized agents — each returning typed Pydantic outputs that downstream systems can consume reliably. No more free-text parsing.

[Start Challenge 1 →](../challenge-1/README.md)
