# MAF Workshop — Infrastructure

Deploys everything needed for the workshop in one `terraform apply`.

## What Gets Deployed

### Tier 1: Notebooks Only (Core Workshop)

| Resource | Type | Purpose |
|----------|------|---------|
| Resource Group | `azurerm_resource_group` | Container for all resources |
| AI Foundry | `Microsoft.CognitiveServices/accounts` (AIServices, S0) | Hosts models + projects |
| Foundry Project | `Microsoft.CognitiveServices/accounts/projects` | Workshop project endpoint |
| GPT-4.1 | `azurerm_cognitive_deployment` (GlobalStandard, capacity 30) | Model used by all agents |
| RBAC: OpenAI User | `azurerm_role_assignment` | Attendees can call the model |
| RBAC: Contributor | `azurerm_role_assignment` | Attendees can manage agents |

### Tier 2: Container Deployment (Bonus Challenge / Demo)

| Resource | Type | Purpose |
|----------|------|---------|
| Container Registry | `Microsoft.ContainerRegistry/registries` (Basic) | Store Docker image |
| Container Apps Environment | `Microsoft.App/managedEnvironments` | Serverless container hosting |
| Container App | `Microsoft.App/containerApps` | Runs the FastAPI incident API |
| Managed Identity | System-assigned on Container App | Passwordless auth to Foundry |
| RBAC: AcrPull | On Container App identity → ACR | Pull images from registry |
| RBAC: OpenAI User | On Container App identity → Foundry | App can call the model |

## What Each Attendee Needs

### In Azure (provisioned by coaches)
- `Cognitive Services OpenAI User` role on the Foundry account
- `Cognitive Services Contributor` role on the Foundry account

### On Their Machine (pre-installed or via Codespaces)
- Python 3.10+
- Azure CLI (`az login` authenticated)
- GitHub Copilot (VS Code extension)

### In Their `.env` File (provided by coaches)
```
FOUNDRY_PROJECT_ENDPOINT=https://<foundry-name>.services.ai.azure.com/api/projects/<project-name>
FOUNDRY_MODEL=gpt-4.1
```

### What's NOT Needed
- ❌ Storage Account
- ❌ Key Vault
- ❌ Azure AI Search
- ❌ API keys (all auth is passwordless via AzureCliCredential)
- ❌ Container Registry (unless deploying the app)
- ❌ GPU or expensive compute

## RBAC Policies

- **Deployer** gets `Cognitive Services OpenAI User` + `Cognitive Services Contributor`
- **Each attendee** gets the same two roles scoped to the Foundry resource
- No API keys — all auth via `az login` + `AzureCliCredential` (passwordless)

## Quick Start

```bash
cd infrastructure
az login
terraform init
terraform plan -var="tags=maf-workshop" -var="region=eastus2"
terraform apply -var="tags=maf-workshop" -var="region=eastus2"
```

## Adding Attendees

Get their Azure AD object IDs:

```bash
az ad user show --id attendee@company.com --query id -o tsv
```

Then pass them as a variable:

```bash
terraform apply \
  -var="tags=maf-workshop" \
  -var='attendee_object_ids=["oid-1","oid-2","oid-3"]'
```

Or create a `terraform.tfvars`:

```hcl
tags = "maf-workshop"
region = "eastus2"
attendee_object_ids = [
  "00000000-0000-0000-0000-000000000001",
  "00000000-0000-0000-0000-000000000002",
]
```

## After Deploy

The outputs give you the `.env` content:

```bash
terraform output ENV_FILE_CONTENT
```

Paste into each attendee's `.env` file (or share in the workshop chat).

## Tear Down

```bash
terraform destroy -var="tags=maf-workshop"
```
