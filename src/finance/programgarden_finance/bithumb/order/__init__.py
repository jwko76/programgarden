"""빗썸 주문(비공개) API - Order 카테고리입니다."""

from typing import Optional

from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from ..models import BithumbCredentials, SetupOptions
from ..tr_helpers import set_tr_options
from . import (
    orders_chance,
    order_detail,
    orders,
    order_new,
    order_cancel,
    order_new_batch,
    order_cancel_batch,
    twap_new,
    twap_cancel,
    twap_list,
)
from .orders_chance import OrdersChanceInBlock, OrdersChanceRequest, TrOrdersChance
from .order_detail import OrderDetailInBlock, OrderDetailRequest, TrOrderDetail
from .orders import OrdersInBlock, OrdersRequest, TrOrders
from .order_new import OrderNewInBlock, OrderNewRequest, TrOrderNew
from .order_cancel import OrderCancelInBlock, OrderCancelRequest, TrOrderCancel
from .order_new_batch import OrderNewBatchInBlock, OrderNewBatchRequest, TrOrderNewBatch
from .order_cancel_batch import OrderCancelBatchInBlock, OrderCancelBatchRequest, TrOrderCancelBatch
from .twap_new import TwapNewInBlock, TwapNewRequest, TrTwapNew
from .twap_cancel import TwapCancelInBlock, TwapCancelRequest, TrTwapCancel
from .twap_list import TwapListInBlock, TwapListRequest, TrTwapList


class Order(metaclass=EnforceKoreanAliasMeta):
    """빗썸 주문(비공개) API 카테고리입니다. 인증(access_key/secret_key)이 필요합니다."""

    def __init__(self, credentials: Optional[BithumbCredentials] = None):
        self.credentials = credentials or BithumbCredentials()

    @require_korean_alias
    def orders_chance(self, params: OrdersChanceInBlock, options: Optional[SetupOptions] = None) -> TrOrdersChance:
        request_data = OrdersChanceRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrOrdersChance(request_data)

    주문가능정보 = orders_chance
    주문가능정보.__doc__ = "마켓별 주문 가능 정보(수수료, 주문 제약, 보유 자산)를 조회합니다."

    @require_korean_alias
    def order_detail(
        self,
        params: OrderDetailInBlock,
        options: Optional[SetupOptions] = None,
    ) -> TrOrderDetail:
        request_data = OrderDetailRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrOrderDetail(request_data)

    개별주문조회 = order_detail
    개별주문조회.__doc__ = "uuid 또는 client_order_id로 개별 주문의 상세 정보(체결 내역 포함)를 조회합니다."

    @require_korean_alias
    def orders(
        self,
        params: Optional[OrdersInBlock] = None,
        options: Optional[SetupOptions] = None,
    ) -> TrOrders:
        request_data = OrdersRequest(params=params or OrdersInBlock())
        set_tr_options(self.credentials, options, request_data)
        return TrOrders(request_data)

    주문리스트조회 = orders
    주문리스트조회.__doc__ = "주문 목록을 조회합니다."

    @require_korean_alias
    def order_new(self, body: OrderNewInBlock, options: Optional[SetupOptions] = None) -> TrOrderNew:
        request_data = OrderNewRequest(body=body)
        set_tr_options(self.credentials, options, request_data)
        return TrOrderNew(request_data)

    주문하기 = order_new
    주문하기.__doc__ = "신규 주문(매수/매도)을 생성합니다."

    @require_korean_alias
    def order_cancel(
        self,
        params: OrderCancelInBlock,
        options: Optional[SetupOptions] = None,
    ) -> TrOrderCancel:
        request_data = OrderCancelRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrOrderCancel(request_data)

    주문취소 = order_cancel
    주문취소.__doc__ = "uuid 또는 client_order_id로 주문을 취소합니다."

    @require_korean_alias
    def order_new_batch(self, body: OrderNewBatchInBlock, options: Optional[SetupOptions] = None) -> TrOrderNewBatch:
        request_data = OrderNewBatchRequest(body=body)
        set_tr_options(self.credentials, options, request_data)
        return TrOrderNewBatch(request_data)

    다건주문 = order_new_batch
    다건주문.__doc__ = "여러 건의 신규 주문(매수/매도)을 한 번에 생성합니다 (최대 20건)."

    @require_korean_alias
    def order_cancel_batch(self, body: OrderCancelBatchInBlock, options: Optional[SetupOptions] = None) -> TrOrderCancelBatch:
        request_data = OrderCancelBatchRequest(body=body)
        set_tr_options(self.credentials, options, request_data)
        return TrOrderCancelBatch(request_data)

    다건주문취소 = order_cancel_batch
    다건주문취소.__doc__ = "order_ids 또는 client_order_ids로 여러 건의 주문을 한 번에 취소합니다 (최대 30건)."

    @require_korean_alias
    def twap_new(self, body: TwapNewInBlock, options: Optional[SetupOptions] = None) -> TrTwapNew:
        request_data = TwapNewRequest(body=body)
        set_tr_options(self.credentials, options, request_data)
        return TrTwapNew(request_data)

    TWAP주문 = twap_new
    TWAP주문.__doc__ = "지정한 시간 동안 일정 간격으로 분할 체결되는 TWAP 주문을 등록합니다."

    @require_korean_alias
    def twap_cancel(self, params: TwapCancelInBlock, options: Optional[SetupOptions] = None) -> TrTwapCancel:
        request_data = TwapCancelRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrTwapCancel(request_data)

    TWAP주문취소 = twap_cancel
    TWAP주문취소.__doc__ = "algo_order_id로 진행 중인 TWAP 주문을 취소합니다."

    @require_korean_alias
    def twap_list(self, params: Optional[TwapListInBlock] = None, options: Optional[SetupOptions] = None) -> TrTwapList:
        request_data = TwapListRequest(params=params or TwapListInBlock())
        set_tr_options(self.credentials, options, request_data)
        return TrTwapList(request_data)

    TWAP주문조회 = twap_list
    TWAP주문조회.__doc__ = "TWAP 주문 목록 및 상태(진행/완료/취소)를 조회합니다."


__all__ = [
    Order,
    orders_chance,
    order_detail,
    orders,
    order_new,
    order_cancel,
    order_new_batch,
    order_cancel_batch,
    twap_new,
    twap_cancel,
    twap_list,
]
