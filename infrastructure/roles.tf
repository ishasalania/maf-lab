# ---------------------------------------------------------------------------
# RBAC Roles — grant access to the deployer + all workshop attendees
# ---------------------------------------------------------------------------

# Deployer (the person running terraform) gets full access
resource "azurerm_role_assignment" "deployer_openai_user" {
  scope                = azapi_resource.foundry.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "deployer_contributor" {
  scope                = azapi_resource.foundry.id
  role_definition_name = "Cognitive Services Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}

# ---------------------------------------------------------------------------
# Attendee access — each attendee gets OpenAI User role
# Populate var.attendee_object_ids with their Azure AD object IDs
# ---------------------------------------------------------------------------

resource "azurerm_role_assignment" "attendee_openai_user" {
  for_each = toset(var.attendee_object_ids)

  scope                = azapi_resource.foundry.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = each.value
}

resource "azurerm_role_assignment" "attendee_contributor" {
  for_each = toset(var.attendee_object_ids)

  scope                = azapi_resource.foundry.id
  role_definition_name = "Cognitive Services Contributor"
  principal_id         = each.value
}
