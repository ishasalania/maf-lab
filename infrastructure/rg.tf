resource "azurerm_resource_group" "this" {
  name     = "${local.resource_name}-rg"
  location = local.location
  tags = {
    Application = var.tags
    Purpose     = "MAF Workshop - WeAreDevelopers 2026"
  }
}
