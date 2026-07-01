data "azurerm_client_config" "current" {}
data "azurerm_subscription" "current" {}

resource "random_pet" "this" {
  length = 2
}

resource "random_id" "this" {
  byte_length = 2
}

locals {
  resource_name  = "maf-${random_pet.this.id}-${random_id.this.dec}"
  foundry_name   = "${local.resource_name}-foundry"
  project_name   = "${local.resource_name}-project"
  location       = var.region
}
