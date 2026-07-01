# ---------------------------------------------------------------------------
# Outputs — used to populate .env files for attendees
# ---------------------------------------------------------------------------

output "FOUNDRY_PROJECT_ENDPOINT" {
  description = "Paste this into .env as FOUNDRY_PROJECT_ENDPOINT"
  value       = "https://${local.foundry_name}.services.ai.azure.com/api/projects/${local.project_name}"
}

output "FOUNDRY_MODEL" {
  description = "Paste this into .env as FOUNDRY_MODEL"
  value       = "gpt-4.1"
}

output "RESOURCE_GROUP" {
  description = "Resource group name"
  value       = azurerm_resource_group.this.name
}

output "SUBSCRIPTION_ID" {
  description = "Azure subscription ID"
  value       = data.azurerm_subscription.current.subscription_id
}

output "ENV_FILE_CONTENT" {
  description = "Ready-to-paste .env file content for attendees"
  value       = <<-EOT
    FOUNDRY_PROJECT_ENDPOINT=https://${local.foundry_name}.services.ai.azure.com/api/projects/${local.project_name}
    FOUNDRY_MODEL=gpt-4.1
  EOT
}

# ---------------------------------------------------------------------------
# Container Deployment Outputs
# ---------------------------------------------------------------------------

output "ACR_LOGIN_SERVER" {
  description = "Container Registry login server (for az acr build)"
  value       = azurerm_container_registry.this.login_server
}

output "ACR_NAME" {
  description = "Container Registry name"
  value       = azurerm_container_registry.this.name
}

output "CONTAINER_APP_URL" {
  description = "Public URL of the deployed API"
  value       = "https://${azurerm_container_app.this.ingress[0].fqdn}"
}

output "DEPLOY_COMMAND" {
  description = "Run this to build and deploy (no Docker needed)"
  value       = "az acr build --registry ${azurerm_container_registry.this.name} --image maf-incident-api:latest ."
}
