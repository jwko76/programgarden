"""키움증권 실시간 주문체결통보 (type "00") 스트림 클라이언트입니다.

KIS의 체결통보는 tr_key로 HTS ID를 쓰고 실전/모의 tr_id가 나뉘지만,
키움은 REG 메시지의 ``item`` 에 계좌번호를 사용한다고 가정하며
실전/모의 type 분기가 없습니다 (도메인 자체가 분기하므로 더 단순합니다).
TODO(실계좌 검증): item 값으로 계좌번호가 맞는지, 빈 값으로도 전체
주문체결을 수신할 수 있는지 확인.
"""

from typing import Any, Callable

from ...config import TR_IDS


class RealOrderNotice:
    """실시간 주문체결통보 구독 클라이언트입니다.

    Example:
        notice = kiwoom.real().order_notice()
        notice.subscribe("12345678")
        notice.on_notice(lambda resp: print(resp.ord_no, resp.ord_stt))
    """

    def __init__(self, parent):
        self._parent = parent

    @property
    def type_code(self) -> str:
        """실시간 주문체결통보 type 코드 ("00")."""
        return TR_IDS.REAL_ORDER_NOTICE

    def subscribe(self, account_no: str) -> None:
        """주문체결통보를 구독합니다. ``account_no`` 는 계좌번호입니다."""
        self._parent._add_keys([account_no], TR_IDS.REAL_ORDER_NOTICE)

    체결통보등록 = subscribe

    def unsubscribe(self, account_no: str) -> None:
        """주문체결통보 구독을 해제합니다."""
        self._parent._remove_keys([account_no], TR_IDS.REAL_ORDER_NOTICE)

    체결통보해제 = unsubscribe

    def on_notice(self, listener: Callable[[Any], Any]) -> None:
        """주문체결통보 메시지 콜백을 등록합니다 (sync/async 모두 허용)."""
        self._parent._on_message(TR_IDS.REAL_ORDER_NOTICE, listener)

    체결통보수신 = on_notice

    def on_remove_notice(self) -> None:
        """주문체결통보 메시지 콜백을 해제합니다."""
        self._parent._on_remove_message(TR_IDS.REAL_ORDER_NOTICE)

    체결통보수신해제 = on_remove_notice
