"""빗썸(Bithumb) TR 요청에서 공통으로 사용하는 모델입니다."""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from .auth import build_authorization_header


class BithumbCredentials(BaseModel):
    """빗썸 API 인증 정보(Access Key / Secret Key)입니다."""

    access_key: Optional[str] = Field(default=None, description="빗썸 API Access Key")
    secret_key: Optional[str] = Field(default=None, description="빗썸 API Secret Key", repr=False)

    def is_available(self) -> bool:
        """access_key와 secret_key가 모두 설정되어 있는지 확인합니다."""
        return bool(self.access_key) and bool(self.secret_key)

    def get_authorization_header(
        self,
        query_params: Optional[dict] = None,
        raw_query_string: Optional[str] = None,
    ) -> str:
        """Private API 호출용 ``Authorization: Bearer <JWT>`` 헤더 값을 생성합니다."""
        return build_authorization_header(self.access_key, self.secret_key, query_params, raw_query_string)


class SetupOptions(BaseModel):
    """TR 요청별 rate-limit 및 인증 정보를 담는 옵션 모델입니다."""

    rate_limit_count: int = Field(default=130, description="허용 요청 횟수 (rate_limit_seconds 내)")
    rate_limit_seconds: int = Field(default=1, description="rate-limit 기준 시간(초)")
    on_rate_limit: Literal["stop", "wait"] = Field(
        default="wait", description="rate-limit 초과 시 동작: 'stop'은 즉시 예외, 'wait'은 대기 후 요청"
    )
    rate_limit_key: Optional[str] = Field(
        default=None, description="여러 TR이 rate-limit 카운터를 공유할 때 사용하는 키"
    )
    credentials: Optional[BithumbCredentials] = Field(
        default=None, exclude=True, repr=False, description="빗썸 API 인증 정보"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


class BithumbErrorBody(BaseModel):
    """빗썸 에러 응답의 ``error`` 객체입니다."""

    name: Optional[str] = Field(default=None, description="에러 코드명", examples=["invalid_access_key"])
    message: Optional[str] = Field(default=None, description="에러 메시지", examples=["No Authorization Key"])


class BithumbResponseBase(BaseModel):
    """모든 빗썸 Response 모델의 공통 필드(상태/에러/원본 응답)입니다."""

    status_code: Optional[int] = Field(default=None, description="HTTP 상태 코드", examples=[200])
    error_name: Optional[str] = Field(default=None, description="빗썸 에러 코드명", examples=["invalid_access_key"])
    error_msg: Optional[str] = Field(default=None, description="에러 메시지 (성공 시 None)")

    _raw_data: Optional[object] = PrivateAttr(default=None)

    @property
    def raw_data(self):
        """원본 HTTP 응답 객체(requests.Response 또는 aiohttp.ClientResponse)입니다."""
        return self._raw_data

    @raw_data.setter
    def raw_data(self, value) -> None:
        self._raw_data = value

    model_config = ConfigDict(arbitrary_types_allowed=True)
