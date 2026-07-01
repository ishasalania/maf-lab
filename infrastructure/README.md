# MAF Workshop — Infrastructure

Deploys everything needed for the workshop in one `terraform apply`.

## What Gets Deployed

| Resource | Type | Purpose |
|----------|------|---------|
| Resource Group | `azurerm_resource_group` | Container for all resources |
| AI Foundry | `Microsoft.CognitiveServices/accounts` (AIServices) | Hosts models + projects |
| Foundry Project | `Microsoft.CognitiveServices/accounts/projects` | Workshop project |
| GPT-4.1 | `azurerm_cognitive_deployment` | Model used by all agents |
| RBAC: OpenAI User | `azurerm_role_assignment` | Attendees can call the model |
| RBAC: Contributor | `azurerm_role_assignment` | Attendees can manage agents |

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
