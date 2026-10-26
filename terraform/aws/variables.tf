variable "region" {
  type        = string
  description = "AWS Region to deploy infrastructure"
  default     = "ap-south-1"
}

variable "cluster_name" {
  type        = string
  description = "EKS Cluster identifier"
  default     = "folio-eks"
}
