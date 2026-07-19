# 계정 현황 파악용 읽기 전용 데이터 소스 (개발서버 셰이프/리전 결정 근거)

data "oci_identity_region_subscriptions" "subs" {
  tenancy_id = var.tenancy_ocid
}

data "oci_core_instances" "existing" {
  compartment_id = local.compartment_id
}

output "region_subscriptions" {
  description = "구독 리전 목록 (is_home_region 포함)"
  value = [
    for r in data.oci_identity_region_subscriptions.subs.region_subscriptions :
    "${r.region_name}${r.is_home_region ? " (home)" : ""}"
  ]
}

output "existing_instances" {
  description = "현재 리전 루트 컴파트먼트의 기존 인스턴스 (셰이프/상태)"
  value = [
    for i in data.oci_core_instances.existing.instances :
    "${i.display_name}: ${i.shape} ${i.shape_config[0].ocpus}ocpu/${i.shape_config[0].memory_in_gbs}gb [${i.state}]"
  ]
}
