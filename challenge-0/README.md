# Challenge 0 — Environment Setup & Resource Deployment

**Expected Duration: 15 minutes**

Welcome to your first challenge! Your goal is to set up the development environment and deploy the Azure resources needed for the workshop. By the end of this challenge, you'll have a working connection to Azure AI Foundry and be ready to build agents.

> **If something is not working, let your coach know immediately!** Don't spend more than 5 minutes stuck on setup.

---

## 1.1 Fork the Repository

Fork this repository to your GitHub account by clicking the **Fork** button in the upper right corner. This lets you save your progress.

---

## 1.2 Development Environment

### Option A: GitHub Codespaces (Recommended)

Click below to open a pre-configured environment with all dependencies installed:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ishasalania/maf-lab?quickstart=1)

> Codespaces gives you Python 3.11, Azure CLI, and all pip packages pre-installed. Zero local setup.

### Option B: Local Setup

```bash
git clone https://github.com/ishasalania/maf-lab.git
cd maf-lab
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

---

## 1.3 Azure Authentication

Log in to Azure CLI:

```bash
az login --use-device-code
```

> This provides a device code and URL. Open the URL in your browser, enter the code, and authenticate. If you have multiple tenants, use: `az login --use-device-code --tenant <TENANT_ID>`

Verify you're logged in:

```bash
az account show
```

---

## 1.4 Resource Deployment

### If your coach pre-provisioned resources:

Your coach will provide you with the following values (on a slide or handout):

```
AZURE_AI_PROJECT_ENDPOINT=https://...
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
```

Copy `.env.example` to `.env` and paste these values:

```bash
cp .env.example .env
```

Then skip to **Section 1.6**.

### If you're deploying your own resources:

Run the deployment script:

```bash
cd challenge-0/scripts
chmod +x deploy-resources.sh get-keys.sh
./deploy-resources.sh --resource-group maf-workshop --location swedencentral
```

Then retrieve your keys:

```bash
./get-keys.sh --resource-group maf-workshop
```

This will:
1. Find your AI Foundry endpoint
2. Assign **Azure AI Developer** and **Cognitive Services User** roles to your account
3. Auto-populate the `.env` file

---

## 1.5 Verify Your Resources

Your resource group should contain:

| Resource | Type | Purpose |
|----------|------|---------|
| AI Foundry Hub | Microsoft.CognitiveServices/AIFoundry | Agent runtime |
| AI Services | Microsoft.CognitiveServices/AIServices | Model hosting |
| GPT-4o deployment | Model Deployment (GlobalStandard) | Powers all agents |

That's it — only 2-3 resources needed for this workshop!

---

## 1.6 Verify Setup

Open `challenge-0/verify-setup.ipynb` and run all cells. You should see:

```
✅ Python 3.11
✅ agent-framework installed
✅ azure-identity installed
✅ python-dotenv installed
✅ Project endpoint: https://...
✅ Model deployment: gpt-4o
✅ Azure CLI authenticated
✅ Agent response: Setup complete!

🎉 ALL CHECKS PASSED — You're ready for the workshop!
```

---

## Success Criteria

- [ ] You can run `az account show` and see your subscription
- [ ] Your `.env` file has `AZURE_AI_PROJECT_ENDPOINT` set
- [ ] `verify-setup.ipynb` runs all cells with green checkmarks
- [ ] You receive a response from the test agent

---

## ➡️ Next Challenge

You're all set! Head to **[Challenge 1: Specialized Agents with Tools](../challenge-1/README.md)** to start building your multi-agent system.
