"""KIS 실시간 WebSocket 클라이언트입니다.

Example:
    kis = Kis()
    kis.login(appkey="...", appsecretkey="...", paper_trading=True)
    real = kis.real()
    await real.connect()
    ccnl = real.ccnl()
    ccnl.add_ccnl_symbols(["005930"])
    ccnl.on_ccnl(lambda resp: print(resp.stck_prpr))
"""

from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from ..real_base import KisRealBase
from .asking_price.client import RealAskingPrice
from .ccnl.client import RealCcnl
from .order_notice.client import RealOrderNotice


class KisReal(KisRealBase, metaclass=EnforceKoreanAliasMeta):
    """KIS 실시간 WebSocket 클라이언트입니다 (tr_id 단위 스트림 구독)."""

    @require_korean_alias
    def ccnl(self) -> RealCcnl:
        """실시간 체결가(H0STCNT0) 스트림 클라이언트를 반환합니다."""
        return RealCcnl(self)

    체결가 = ccnl
    체결가.__doc__ = "실시간 체결가(H0STCNT0) 스트림 클라이언트를 반환합니다."

    @require_korean_alias
    def asking_price(self) -> RealAskingPrice:
        """실시간 호가(H0STASP0) 스트림 클라이언트를 반환합니다."""
        return RealAskingPrice(self)

    호가 = asking_price
    호가.__doc__ = "실시간 호가(H0STASP0) 스트림 클라이언트를 반환합니다."

    @require_korean_alias
    def order_notice(self) -> RealOrderNotice:
        """실시간 체결통보(H0STCNI0/H0STCNI9) 스트림 클라이언트를 반환합니다."""
        return RealOrderNotice(self, self._token_manager.paper_trading)

    체결통보 = order_notice
    체결통보.__doc__ = "실시간 체결통보(H0STCNI0/H0STCNI9) 스트림 클라이언트를 반환합니다."


__all__ = [
    KisReal,
    RealCcnl,
    RealAskingPrice,
    RealOrderNotice,
]
