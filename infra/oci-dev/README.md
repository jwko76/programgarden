# OCI 개발서버 (programgarden-dev)

키움·빗썸 등 **IP 화이트리스트가 걸린 브로커 API의 라이브 검증**을 실행하는
전용 개발서버. MonitoringLSStock 운영서버(OCI)와 같은 테넌시에 Terraform으로
프로비저닝한다 (로컬 PC IP는 유동이라 화이트리스트 운용이 불가능해서 분리).

## 스펙

| 항목 | 값 |
|------|-----|
| 리전 | ap-osaka-1 (테넌시 홈 리전, 단일 구독) |
| 셰이프 | VM.Standard.A1.Flex — 2 OCPU / 12GB (Always Free 한도 내, 운영 1/6 사용 후 잔여분) |
| OS | Canonical Ubuntu 24.04 (aarch64) — Python 3.12 기본 탑재 |
| 퍼블릭 IP | **Reserved(고정)** — 인스턴스 재생성에도 유지. 키움 지정단말기·빗썸 화이트리스트에 이 IP를 등록 |
| SSH | 22 포트, terraform.tfvars의 `ssh_ingress_cidr`(내 IP/32)만 허용 |
| 키 | `~/.ssh/oci_dev` (로컬 Windows·WSL 공용, 커밋 금지) |

## 자주 쓰는 명령 (이 디렉터리에서)

```bash
terraform output -raw instance_public_ip    # 서버 고정 IP 확인
ssh -i ~/.ssh/oci_dev ubuntu@$(terraform output -raw instance_public_ip)

# 로컬 코드 → 서버 동기화 (WSL)
rsync -az --delete -e 'ssh -i ~/.ssh/oci_dev' \
  --exclude .git --exclude .env --exclude '__pycache__' --exclude '.venv*' \
  --exclude 'infra/' --exclude '*.pyc' --exclude '.pytest_cache' \
  /mnt/d/Work/VisualStudio/programgarden/ ubuntu@<IP>:~/programgarden/

# 서버에서 검증 실행
cd ~/programgarden
KIWOOM_PAPER=1 .venv/bin/python src/finance/example/kiwoom/run_quotations.py
.venv/bin/python -m pytest src/finance/tests/ -q
```

## 서버 구성 내역 (2026-07-19 프로비저닝)

- `~/programgarden/` — 로컬 워킹트리 rsync 사본 (.git 미포함)
- `~/programgarden/.venv` — Python 3.12 venv, core+finance editable install
  + python-dotenv/pytest/pytest-asyncio/requests-mock
- `~/programgarden/.env` — 로컬 .env를 scp로 이식 (chmod 600). **내용 열람·출력 금지**

## 변경/관리

- 스펙 변경: `terraform.tfvars` 수정 → `terraform apply`
- 중지/기동: `oci_core_instance.vm`에 `state = "STOPPED"`/`"RUNNING"` 추가 후 apply
- 폐기: `terraform destroy` (Reserved IP도 함께 해제되므로 화이트리스트 재등록 필요 — 주의)
- 내 IP가 바뀌어 SSH가 막히면: `ssh_ingress_cidr` 갱신 후 apply

## 보안 규칙

- `terraform.tfvars`(OCID·키 경로)와 `*.tfstate`(전체 리소스 상태)는 gitignore — 커밋 금지
- API 키·.env 내용은 어떤 로그·채팅에도 출력하지 않는다
- SSH ingress는 항상 내 IP/32로 제한 (0.0.0.0/0 금지)
- OCI API 키는 `C:\Users\user\.oci\oci_api_key.pem` — 경로로만 참조

## 화이트리스트 등록 (사용자 수동, 1회)

서버 고정 IP(`terraform output -raw instance_public_ip`)를 다음 두 곳에 등록:
1. 키움 OpenAPI → 지정단말기(IP) 관리 — 실전 API용
2. 빗썸 → API 키 설정 → 허용 IP 추가
(운영서버 IP가 이미 등록돼 있다면 **추가**로 등록 — 교체 아님)
