"""한국투자증권(KIS) TR 요청에서 공통으로 사용하는 모델입니다."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


class SetupOptions(BaseModel):
    """TR 요청별 rate-limit 및 인증 정보를 담는 옵션 모델입니다.

    KIS rate-limit: 실전 초당 20건, 모의 초당 2건 (appkey 기준).
    ``token_manager`` 는 클라이언트가 주입하며 모든 TR이 공유합니다.
    """

    rate_limit_count: int = Field(default=20, description="허용 요청 횟수 (rate_limit_seconds 내)")
    rate_limit_seconds: int = Field(default=1, description="rate-limit 기준 시간(초)")
    on_rate_limit: Literal["stop", "wait"] = Field(
        default="wait", description="rate-limit 초과 시 동작: 'stop'은 즉시 예외, 'wait'은 대기 후 요청"
    )
    rate_limit_key: Optional[str] = Field(
        default=None, description="여러 TR이 rate-limit 카운터를 공유할 때 사용하는 키"
    )
    token_manager: Optional[Any] = Field(
        default=None, exclude=True, repr=False, description="KisTokenManager (클라이언트가 주입)"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def for_mode(cls, paper_trading: bool, appkey: Optional[str] = None) -> "SetupOptions":
        """실전/모의 모드에 맞는 기본 rate-limit 옵션을 생성합니다.

        appkey가 주어지면 같은 계정의 모든 TR이 rate-limit 버킷을 공유합니다.
        """
        return cls(
            rate_limit_count=2 if paper_trading else 20,
            rate_limit_seconds=1,
            rate_limit_key=f"kis:{appkey}" if appkey else None,
        )


class KisResponseBase(BaseModel):
    """모든 KIS Response 모델의 공통 필드입니다.

    KIS 응답 봉투: ``rt_cd``("0"=성공), ``msg_cd``, ``msg1`` + output/output1/output2.
    """

    status_code: Optional[int] = Field(default=None, description="HTTP 상태 코드", examples=[200])
    rt_cd: Optional[str] = Field(default=None, description="성공 여부 코드 (0=성공)", examples=["0"])
    msg_cd: Optional[str] = Field(default=None, description="응답 메시지 코드", examples=["MCA00000"])
    msg1: Optional[str] = Field(default=None, description="응답 메시지")
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
