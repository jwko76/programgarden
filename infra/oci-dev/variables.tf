# --- Authentication (fill values in terraform.tfvars) ---

variable "tenancy_ocid" {
  type        = string
  description = "OCID of the tenancy (root compartment)."
}

variable "user_ocid" {
  type        = string
  description = "OCID of the IAM user used for API access."
}

variable "fingerprint" {
  type        = string
  description = "Fingerprint of the uploaded API public key."
}

variable "private_key_path" {
  type        = string
  description = "Local filesystem path to the API private key (.pem)."
}

variable "region" {
  type        = string
  description = "OCI region identifier, e.g. ap-osaka-1."
}

# --- Where to create resources ---

variable "compartment_ocid" {
  type        = string
  description = "Compartment for resources. Empty string = tenancy root."
  default     = ""
}

# --- VM configuration ---

variable "instance_name" {
  type        = string
  description = "Display name for the compute instance."
  default     = "tf-vm"
}

variable "instance_shape" {
  type        = string
  description = "Compute shape. Free tier: VM.Standard.A1.Flex or VM.Standard.E2.1.Micro."
  default     = "VM.Standard.A1.Flex"
}

variable "instance_ocpus" {
  type        = number
  description = "OCPUs for flex shapes (ignored by fixed shapes like E2.1.Micro)."
  default     = 2
}

variable "instance_memory_gbs" {
  type        = number
  description = "Memory in GB for flex shapes."
  default     = 12
}

variable "image_os" {
  type        = string
  description = "Operating system for the image lookup."
  default     = "Canonical Ubuntu"
}

variable "image_os_version" {
  type        = string
  description = "OS version for the image lookup."
  default     = "22.04"
}

variable "ssh_public_key_path" {
  type        = string
  description = "Path to the SSH public key used for instance login."
  default     = "~/.ssh/oci_vm.pub"
}

variable "ssh_ingress_cidr" {
  type        = string
  description = "CIDR allowed to reach port 22. Tighten to your IP/32 outside testing."
  default     = "0.0.0.0/0"
}
