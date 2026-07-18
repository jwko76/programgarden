"""키움증권(Kiwoom Securities) TR 요청에서 공통으로 사용하는 모델입니다."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


class SetupOptions(BaseModel):
    """TR 요청별 rate-limit 및 인증 정보를 담는 옵션 모델입니다.

    키움 rate-limit 정책은 공식 문서로 확인되지 않아, KIS 실전 기준(초당
    20건)을 보수적으로 차용한 추정치입니다.
    TODO(실계좌 검증): 정확한 rate-limit 정책 확인 후 조정.
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
        default=None, exclude=True, repr=False, description="KiwoomTokenManager (클라이언트가 주입)"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def for_mode(cls, paper_trading: bool, appkey: Optional[str] = None) -> "SetupOptions":
        """실전/모의 모드에 맞는 기본 rate-limit 옵션을 생성합니다.

        appkey가 주어지면 같은 계정의 모든 TR이 rate-limit 버킷을 공유합니다.
        키움은 실전/모의가 도메인 단위로 분기되므로, rate_limit_count 자체는
        모드에 따라 달라지지 않는다고 가정합니다.
        TODO(실계좌 검증): 모의투자 rate-limit이 실전과 다른지 확인.
        """
        return cls(
            rate_limit_count=20,
            rate_limit_seconds=1,
            rate_limit_key=f"kiwoom:{appkey}" if appkey else None,
        )


class KiwoomResponseBase(BaseModel):
    """모든 Kiwoom Response 모델의 공통 필드입니다.

    키움 응답 봉투: ``return_code``(0=성공), ``return_msg`` — KIS의
    ``rt_cd``/``msg_cd``/``msg1`` 3분할과 달리 코드 하나 + 메시지 하나이며,
    KIS의 output/output1/output2 같은 별도 데이터 봉투 키도 없습니다.
    """

    status_code: Optional[int] = Field(default=None, description="HTTP 상태 코드", examples=[200])
    return_code: Optional[int] = Field(default=None, description="성공 여부 코드 (0=성공)", examples=[0])
    return_msg: Optional[str] = Field(default=None, description="응답 메시지")
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
