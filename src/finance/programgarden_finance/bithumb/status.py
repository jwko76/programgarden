from enum import Enum


class RequestStatus(Enum):
    """
    요청 상태를 나타내는 Enum 클래스입니다.
    - REQUEST: 요청이 진행 중
    - OCCURS_REQUEST: 추가 데이터 요청
    - RESPONSE: 데이터 응답
    - COMPLETE: 모든 데이터 요청/응답 완료
    - FAIL: 요청 실패
    - CLOSE: 종료
    """

    REQUEST = "request"
    OCCURS_REQUEST = "occurs_request"
    RESPONSE = "response"
    COMPLETE = "complete"
    FAIL = "fail"
    CLOSE = "close"
