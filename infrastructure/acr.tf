# ---------------------------------------------------------------------------
# Azure Container Registry — builds images in the cloud (no local Docker needed)
# ---------------------------------------------------------------------------

resource "azurerm_container_registry" "this" {
  name                = replace("${local.resource_name}acr", "-", "")
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  sku                 = "Basic"
  admin_enabled       = false

  tags = {
    Application = var.tags
  }
}

# Allow Container App managed identity to pull images
resource "azurerm_role_assignment" "aca_acr_pull" {
  scope                = azurerm_container_registry.this.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.aca_identity.principal_id
}

# Allow deployer to push images
resource "azurerm_role_assignment" "deployer_acr_push" {
  scope                = azurerm_container_registry.this.id
  role_definition_name = "AcrPush"
  principal_id         = data.azurerm_client_config.current.object_id
}
