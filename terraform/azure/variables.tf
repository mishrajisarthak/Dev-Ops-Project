variable "location" {
  type        = string
  description = "Azure region for all provisioned resources"
  default     = "eastus"
}

variable "resource_group_name" {
  type        = string
  description = "Dedicated isolated resource group name"
  default     = "rg-folio-capstone"
}

variable "cluster_name" {
  type        = string
  description = "Name of the managed AKS cluster"
  default     = "aks-folio"
}

variable "vm_size" {
  type        = string
  description = "Virtual machine SKU for AKS worker nodes"
  default     = "Standard_B2s"
}

variable "node_count" {
  type        = number
  description = "Initial number of worker nodes"
  default     = 2
}
