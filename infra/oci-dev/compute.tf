##############################################################################
# Locals: default to tenancy root compartment when none is given.
##############################################################################
locals {
  compartment_id = var.compartment_ocid != "" ? var.compartment_ocid : var.tenancy_ocid
}

##############################################################################
# Lookups: availability domain + latest matching image.
# Using data sources avoids hardcoding region-specific OCIDs.
##############################################################################
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

data "oci_core_images" "os" {
  compartment_id           = local.compartment_id
  operating_system         = var.image_os
  operating_system_version = var.image_os_version
  shape                    = var.instance_shape
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

# --- Auth smoke test (read-only). A successful plan proves credentials work. ---
data "oci_objectstorage_namespace" "ns" {
  compartment_id = var.tenancy_ocid
}

##############################################################################
# Networking: a minimal VCN with an internet-facing public subnet.
##############################################################################
resource "oci_core_vcn" "vcn" {
  compartment_id = local.compartment_id
  cidr_blocks    = ["10.0.0.0/16"]
  display_name   = "${var.instance_name}-vcn"
  dns_label      = "vcn"
}

resource "oci_core_internet_gateway" "igw" {
  compartment_id = local.compartment_id
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "${var.instance_name}-igw"
}

resource "oci_core_route_table" "rt" {
  compartment_id = local.compartment_id
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "${var.instance_name}-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.igw.id
  }
}

resource "oci_core_security_list" "sl" {
  compartment_id = local.compartment_id
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "${var.instance_name}-sl"

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }

  # SSH
  ingress_security_rules {
    protocol = "6" # TCP
    source   = var.ssh_ingress_cidr
    tcp_options {
      min = 22
      max = 22
    }
  }
}

resource "oci_core_subnet" "subnet" {
  compartment_id    = local.compartment_id
  vcn_id            = oci_core_vcn.vcn.id
  cidr_block        = "10.0.1.0/24"
  display_name      = "${var.instance_name}-subnet"
  dns_label         = "subnet"
  route_table_id    = oci_core_route_table.rt.id
  security_list_ids = [oci_core_security_list.sl.id]
}

##############################################################################
# The compute instance.
##############################################################################
resource "oci_core_instance" "vm" {
  compartment_id      = local.compartment_id
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = var.instance_name
  shape               = var.instance_shape

  # shape_config only applies to flexible shapes. Harmless to include; fixed
  # shapes (E2.1.Micro) ignore mismatched values but to be safe set OCPUs to 1
  # for that shape via terraform.tfvars.
  shape_config {
    ocpus         = var.instance_ocpus
    memory_in_gbs = var.instance_memory_gbs
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.os.images[0].id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.subnet.id
    assign_public_ip = false # 고정 IP는 아래 reserved public IP로 부여
  }

  metadata = {
    ssh_authorized_keys = file(var.ssh_public_key_path)
  }
}

##############################################################################
# Reserved public IP — 인스턴스 재생성에도 유지되는 고정 IP.
# 키움 지정단말기·빗썸 IP 화이트리스트에 등록하므로 반드시 고정이어야 한다.
##############################################################################
data "oci_core_vnic_attachments" "vm" {
  compartment_id = local.compartment_id
  instance_id    = oci_core_instance.vm.id
}

data "oci_core_private_ips" "vm" {
  vnic_id = data.oci_core_vnic_attachments.vm.vnic_attachments[0].vnic_id
}

resource "oci_core_public_ip" "reserved" {
  compartment_id = local.compartment_id
  lifetime       = "RESERVED"
  display_name   = "${var.instance_name}-reserved-ip"
  private_ip_id  = [for p in data.oci_core_private_ips.vm.private_ips : p.id if p.is_primary][0]
}

##############################################################################
# Outputs
##############################################################################
output "auth_check_namespace" {
  description = "Object Storage namespace — presence confirms auth succeeded."
  value       = data.oci_objectstorage_namespace.ns.namespace
}

output "instance_public_ip" {
  description = "Reserved public IP of the VM. SSH: ssh -i ~/.ssh/oci_dev ubuntu@<ip>"
  value       = oci_core_public_ip.reserved.ip_address
}

output "instance_id" {
  value = oci_core_instance.vm.id
}
