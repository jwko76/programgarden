# ProgramGarden — 시큐어 코딩 규칙

모든 기여자와 Claude는 이 파일의 규칙을 **구현마다** 준수해야 합니다.
코드 리뷰 및 PR 병합 전 이 체크리스트를 확인하세요.

---

## 1. 입력 검증 (Input Validation)

### 1.1 외부 경계에서만 검증
- 사용자 입력, 외부 API 응답, 환경변수는 **시스템 경계**에서 즉시 검증
- 내부 함수 간 호출은 Pydantic 모델이 보장하므로 중복 검증 불필요

### 1.2 Pydantic 타입 강제
```python
# ✅ 올바른 예 — Pydantic Literal로 열거값 제한
side: Literal["bid", "ask"] = Field(...)

# ❌ 잘못된 예 — 런타임에 if 분기로 직접 검사
if side not in ("bid", "ask"):
    raise ValueError(...)
```

### 1.3 문자열 패턴 제한
- 마켓 코드: `^[A-Z]+-[A-Z0-9]+$` (예: `KRW-BTC`)
- 심볼 코드: `^[A-Z0-9]{1,20}$`
- 날짜: `^\d{4}-\d{2}-\d{2}$` 또는 `^\d{8}$`

### 1.4 숫자 범위
```python
count: int = Field(default=30, ge=1, le=200)  # ge/le로 범위 강제
```

---

## 2. 인증 · 인가 (Authentication & Authorization)

### 2.1 모든 Private API는 인증 필수
- LS 증권 Private TR: `access_key` / `secret_key` 없이 호출 금지
- 빗썸 Private API: JWT 서명 검증 후 호출
- 공개 API(`/v1/ticker`, `/v1/candles/*`)만 인증 없이 사용 가능

### 2.2 소유권 검사
```python
# ✅ 올바른 예 — user_id로 소유권 확인
result = await db.execute(
    select(AlertRule).where(AlertRule.id == rule_id, AlertRule.user_id == current_user.id)
)
# ❌ 잘못된 예 — ID만으로 조회 (다른 사용자 데이터 접근 가능)
result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
```

### 2.3 JWT 토큰
- 서명 알고리즘: HS256 (SECRET_KEY 필수)
- 만료시간: 8시간 이내
- HttpOnly SameSite=Lax 쿠키로 전달 (JS 접근 차단)

---

## 3. SQL 인젝션 방지

### 3.1 ORM 파라미터화 쿼리만 사용
```python
# ✅ ORM — 자동 파라미터화
await db.execute(select(User).where(User.username == username))

# ✅ text() 사용 시 바인딩 필수
await db.execute(text("SELECT * FROM users WHERE id = :uid"), {"uid": user_id})

# ❌ 절대 금지 — f-string 직접 삽입
await db.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### 3.2 `text()` 최소화
- 가급적 ORM 표현식 사용
- `text()` 불가피할 경우 `:param` 바인딩 변수만 허용

---

## 4. XSS 방지

### 4.1 Jinja2 자동 이스케이프 유지
- `{% autoescape true %}` 비활성화 금지
- `{{ value | safe }}` 필터는 HTML 생성 함수(`Markup()`) 반환값에만 허용

### 4.2 JSON API 응답
```python
# ✅ FastAPI JSONResponse 사용 — 자동 이스케이프
return JSONResponse({"name": user_input})

# ❌ 문자열 직접 조합
return Response(f'{{"name": "{user_input}"}}', media_type="application/json")
```

### 4.3 JavaScript 동적 DOM
```javascript
// ✅ textContent — 텍스트로 삽입 (XSS 없음)
el.textContent = data.name;

// ❌ innerHTML — 사용자 입력 직접 삽입 금지
el.innerHTML = data.name;
```

---

## 5. 시크릿 관리 (Secrets Management)

### 5.1 하드코딩 금지
```python
# ❌ 절대 금지
SECRET_KEY = "my-hardcoded-secret"
APPKEY = "ghp_xxxxxxxxxxx"

# ✅ 환경변수에서 로드
SECRET_KEY = os.environ["SECRET_KEY"]
```

### 5.2 로그에 시크릿 출력 금지
```python
# ❌ 절대 금지
logger.info(f"Connecting with key={access_key}")

# ✅ 마스킹
logger.info(f"Connecting with key=****{access_key[-4:]}")
```

### 5.3 Git 커밋 금지 파일
- `.env`, `ec2.conf`, `*.pem`, `*.ppk`, `github_PAT*`
- 위 파일들은 `.gitignore`에 등록 완료

### 5.4 DB 암호화 저장
```python
# LS증권 appsecret — Fernet 대칭 암호화 후 DB 저장
appsecret_enc: Mapped[str] = mapped_column(String(500))
```

---

## 6. Rate Limiting & DoS 방지

### 6.1 LS증권 TR Rate Limit
```python
SetupOptions(
    rate_limit_count=1,
    rate_limit_seconds=1,
    on_rate_limit="wait",   # "error" 아님 — 재시도 자동 대기
)
```

### 6.2 주문 중복 방지
- `BithumbNewOrderNode` / `OverseasStock*NewOrderNode`: 기본 retry 비활성화
- 최대 재시도 횟수: 3회 상한

### 6.3 WebSocket 재연결 백오프
- 지수 백오프 (1s → 2s → 4s → 최대 60s)
- 연속 실패 시 알림 발송

---

## 7. 에러 처리 & 로깅

### 7.1 상세 에러를 외부에 노출 금지
```python
# ✅ 내부 로그에 상세, 외부에 일반 메시지
logger.error(f"DB error: {exc!r}")
raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

# ❌ 스택 트레이스 외부 노출
raise HTTPException(status_code=500, detail=str(exc))
```

### 7.2 민감 필드 로그 제외
- `password`, `access_key`, `secret_key`, `appsecret`, `token` 포함 로그 금지

### 7.3 구조화 로그
```python
logger.info("[BithumbNewOrder] %s %s %s vol=%s", market, side, order_type, volume)
```

---

## 8. 의존성 보안

### 8.1 버전 고정
- `requirements.txt`: `==` 핀 사용
- `pyproject.toml`: `>=X.Y.Z,<X+1` 범위 사용

### 8.2 알려진 취약점 점검
```bash
pip audit   # 의존성 CVE 검사
```

---

## 체크리스트 (구현 완료 시 확인)

- [ ] 사용자 입력에 Pydantic 타입/범위 검증 적용
- [ ] 모든 DB 조회에 `user_id` 소유권 조건 포함
- [ ] `text()` SQL 사용 시 `:param` 바인딩 확인
- [ ] Jinja2 템플릿에서 `| safe` 오용 없음
- [ ] JS에서 `innerHTML`에 사용자 데이터 미사용
- [ ] 환경변수/시크릿 하드코딩 없음
- [ ] 로그에 키/패스워드 미출력
- [ ] Rate limit / retry 설정 적절
- [ ] 에러 메시지 외부 노출 없음
