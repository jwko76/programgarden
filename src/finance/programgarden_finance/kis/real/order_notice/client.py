"""KIS 실시간 체결통보 (H0STCNI0/H0STCNI9) 스트림 클라이언트입니다.

``tr_key`` 는 종목코드가 아닌 **HTS ID** 입니다. 실전(H0STCNI0)/모의(H0STCNI9)
tr_id는 클라이언트의 paper_trading 설정으로 자동 선택됩니다.
데이터는 AES-256-CBC 암호문으로 수신되며 구독 응답의 key/iv로 복호화됩니다.
"""

from typing import Any, Callable

from ...config import TR_IDS


class RealOrderNotice:
    """실시간 체결통보 구독 클라이언트입니다.

    Example:
        notice = kis.real().order_notice()
        notice.subscribe("my_hts_id")
        notice.on_notice(lambda resp: print(resp.oder_no, resp.cntg_yn))
    """

    def __init__(self, parent, paper_trading: bool):
        self._parent = parent
        real_id, paper_id = TR_IDS.REAL_ORDER_NOTICE
        self._tr_id = paper_id if paper_trading else real_id

    @property
    def tr_id(self) -> str:
        """실전/모의 모드에 따라 결정된 tr_id (H0STCNI0/H0STCNI9)."""
        return self._tr_id

    def subscribe(self, hts_id: str) -> None:
        """체결통보를 구독합니다. ``hts_id`` 는 HTS 로그인 ID입니다."""
        self._parent._add_keys([hts_id], self._tr_id)

    체결통보등록 = subscribe

    def unsubscribe(self, hts_id: str) -> None:
        """체결통보 구독을 해제합니다."""
        self._parent._remove_keys([hts_id], self._tr_id)

    체결통보해제 = unsubscribe

    def on_notice(self, listener: Callable[[Any], Any]) -> None:
        """체결통보 메시지 콜백을 등록합니다 (sync/async 모두 허용)."""
        self._parent._on_message(self._tr_id, listener)

    체결통보수신 = on_notice

    def on_remove_notice(self) -> None:
        """체결통보 메시지 콜백을 해제합니다."""
        self._parent._on_remove_message(self._tr_id)

    체결통보수신해제 = on_remove_notice
