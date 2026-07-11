from enum import Enum


class RequestStatus(Enum):
    """
    TR 요청의 상태를 나타내는 열거형입니다.
    """
    REQUEST = "request"
    """요청 발생"""
    OCCURS_REQUEST = "occurs_request"
    """연속 조회 요청 발생"""
    RESPONSE = "response"
    """응답 발생"""
    COMPLETE = "complete"
    """모든 결과값 완료"""
    FAIL = "fail"
    """실패"""
    CLOSE = "close"
    """모든 종료"""
