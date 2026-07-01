variable "region" {
  description = "Azure region to deploy resources"
  default     = "eastus2"
}

variable "tags" {
  description = "Tags to apply to all resources"
  default     = "maf-workshop"
}

variable "attendee_object_ids" {
  description = "List of Azure AD object IDs for workshop attendees (from `az ad user show --id <email> --query id -o tsv`)"
  type        = list(string)
  default     = []
}
