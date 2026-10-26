resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  location            = azurerm_resource_group.folio.location
  resource_group_name = azurerm_resource_group.folio.name
  dns_prefix          = "folio-k8s"

  default_node_pool {
    name           = "system"
    node_count     = var.node_count
    vm_size        = var.vm_size
    vnet_subnet_id = azurerm_subnet.aks.id

    os_disk_size_gb = 30
    os_disk_type    = "Managed"

    tags = azurerm_resource_group.folio.tags
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "kubenet"
    load_balancer_sku = "standard"
  }

  tags = azurerm_resource_group.folio.tags
}
