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
