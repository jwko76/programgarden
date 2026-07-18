"""키움증권 실시간 WebSocket 클라이언트입니다.

Example:
    kiwoom = Kiwoom()
    kiwoom.login(appkey="...", appsecretkey="...", paper_trading=True)
    real = kiwoom.real()
    await real.connect()
    ccnl = real.ccnl()
    ccnl.add_ccnl_symbols(["005930"])
    ccnl.on_ccnl(lambda resp: print(resp.cur_prc))
"""

from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from ..real_base import KiwoomRealBase
from .ccnl.client import RealCcnl
from .order_notice.client import RealOrderNotice


class KiwoomReal(KiwoomRealBase, metaclass=EnforceKoreanAliasMeta):
    """키움증권 실시간 WebSocket 클라이언트입니다 (type 단위 스트림 구독)."""

    @require_korean_alias
    def ccnl(self) -> RealCcnl:
        """실시간 주식체결(0B) 스트림 클라이언트를 반환합니다."""
        return RealCcnl(self)

    체결가 = ccnl
    체결가.__doc__ = "실시간 주식체결(0B) 스트림 클라이언트를 반환합니다."

    @require_korean_alias
    def order_notice(self) -> RealOrderNotice:
        """실시간 주문체결통보(00) 스트림 클라이언트를 반환합니다."""
        return RealOrderNotice(self)

    체결통보 = order_notice
    체결통보.__doc__ = "실시간 주문체결통보(00) 스트림 클라이언트를 반환합니다."


__all__ = [
    KiwoomReal,
    RealCcnl,
    RealOrderNotice,
]
