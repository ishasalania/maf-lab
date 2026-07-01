# ---------------------------------------------------------------------------
# Azure AI Foundry (AIServices account with project management enabled)
# This is the single resource that hosts models + projects for the workshop.
# ---------------------------------------------------------------------------

resource "azapi_resource" "foundry" {
  type      = "Microsoft.CognitiveServices/accounts@2025-06-01"
  name      = local.foundry_name
  location  = azurerm_resource_group.this.location
  parent_id = azurerm_resource_group.this.id

  identity {
    type = "SystemAssigned"
  }

  body = {
    sku = {
      name = "S0"
    }
    kind = "AIServices"
    properties = {
      allowProjectManagement = true
      customSubDomainName    = local.foundry_name
      publicNetworkAccess    = "Enabled"
    }
  }

  tags = {
    Application = var.tags
  }
}

# ---------------------------------------------------------------------------
# Foundry Project — one project for the entire workshop
# ---------------------------------------------------------------------------

resource "azapi_resource" "foundry_project" {
  type      = "Microsoft.CognitiveServices/accounts/projects@2025-06-01"
  name      = local.project_name
  location  = azurerm_resource_group.this.location
  parent_id = azapi_resource.foundry.id

  identity {
    type = "SystemAssigned"
  }

  body = {
    properties = {
      displayName = local.project_name
    }
  }
}

# ---------------------------------------------------------------------------
# Model Deployment — GPT-4.1 (primary model for the workshop)
# ---------------------------------------------------------------------------

resource "azurerm_cognitive_deployment" "gpt_41" {
  name                 = "gpt-4.1"
  cognitive_account_id = azapi_resource.foundry.id

  model {
    format = "OpenAI"
    name   = "gpt-4.1"
  }

  sku {
    name     = "GlobalStandard"
    capacity = 30
  }
}
