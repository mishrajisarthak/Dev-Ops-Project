output "resource_group_name" {
  value       = azurerm_resource_group.folio.name
  description = "The isolated resource group name"
}

output "aks_cluster_name" {
  value       = azurerm_kubernetes_cluster.aks.name
  description = "The deployed AKS cluster name"
}

output "kube_config_command" {
  value       = "az aks get-credentials --resource-group ${azurerm_resource_group.folio.name} --name ${azurerm_kubernetes_cluster.aks.name} --overwrite-existing"
  description = "Command to configure local kubectl to connect to the AKS cluster"
}

output "oidc_issuer_url" {
  value       = azurerm_kubernetes_cluster.aks.oidc_issuer_url
  description = "The OIDC issuer URL for workload identity"
}
