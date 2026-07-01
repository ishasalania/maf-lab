# ---------------------------------------------------------------------------
# Azure Container Apps — serverless deployment of the MAF Incident API
# ---------------------------------------------------------------------------

resource "azurerm_user_assigned_identity" "aca_identity" {
  name                = "${local.resource_name}-aca-identity"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
}

# Container App identity needs to call the Foundry model
resource "azurerm_role_assignment" "aca_openai_user" {
  scope                = azapi_resource.foundry.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azurerm_user_assigned_identity.aca_identity.principal_id
}

resource "azurerm_role_assignment" "aca_contributor" {
  scope                = azapi_resource.foundry.id
  role_definition_name = "Cognitive Services Contributor"
  principal_id         = azurerm_user_assigned_identity.aca_identity.principal_id
}

resource "azurerm_container_app_environment" "this" {
  name                = "${local.resource_name}-env"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name

  tags = {
    Application = var.tags
  }
}

resource "azurerm_container_app" "this" {
  name                         = "${local.resource_name}-app"
  container_app_environment_id = azurerm_container_app_environment.this.id
  resource_group_name          = azurerm_resource_group.this.name
  revision_mode                = "Single"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.aca_identity.id]
  }

  registry {
    server   = azurerm_container_registry.this.login_server
    identity = azurerm_user_assigned_identity.aca_identity.id
  }

  template {
    min_replicas = 0
    max_replicas = 3

    container {
      name   = "maf-api"
      image  = "${azurerm_container_registry.this.login_server}/maf-incident-api:latest"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "FOUNDRY_PROJECT_ENDPOINT"
        value = "https://${local.foundry_name}.services.ai.azure.com/api/projects/${local.project_name}"
      }

      env {
        name  = "FOUNDRY_MODEL"
        value = "gpt-4.1"
      }

      env {
        name  = "AZURE_CLIENT_ID"
        value = azurerm_user_assigned_identity.aca_identity.client_id
      }

      liveness_probe {
        transport = "HTTP"
        path      = "/health"
        port      = 8000
      }

      readiness_probe {
        transport = "HTTP"
        path      = "/health"
        port      = 8000
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  tags = {
    Application = var.tags
  }
}
