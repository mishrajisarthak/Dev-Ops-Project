terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  features {}
}

# Dedicated isolated resource group for Folio Capstone
resource "azurerm_resource_group" "folio" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Environment = "Capstone"
    Project     = "Folio-Library"
    ManagedBy   = "Terraform"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "folio" {
  name                = "vnet-folio"
  location            = azurerm_resource_group.folio.location
  resource_group_name = azurerm_resource_group.folio.name
  address_space       = ["10.10.0.0/16"]

  tags = azurerm_resource_group.folio.tags
}

# Dedicated Subnet for AKS Cluster
resource "azurerm_subnet" "aks" {
  name                 = "snet-folio-aks"
  resource_group_name  = azurerm_resource_group.folio.name
  virtual_network_name = azurerm_virtual_network.folio.name
  address_prefixes     = ["10.10.1.0/24"]
}
