"""Google Maps Places API Tools for PlacesAgent using Google Cloud Client Library."""

import logging
import os
from datetime import datetime
from typing import Any, Dict

from google.adk.tools import ToolContext
from google.api_core import client_options
from google.api_core.exceptions import (GoogleAPIError, InvalidArgument,
                                        PermissionDenied, ResourceExhausted)
from google.maps import places_v1
from google.maps.places_v1.types import Place, PriceLevel, SearchTextRequest

# 로거 설정
logger = logging.getLogger(__name__)

# 상수 정의
DEFAULT_FIELDS = "places.id,places.attributions,places.displayName,places.formattedAddress,places.location"


class PlacesService:
    """
    Google Maps Places API를 위한 포괄적인 래퍼 클래스입니다.

    Google Cloud Client Library를 사용하여 Places API의 기능들을 제공하며,
    텍스트 검색, 필드 마스킹, 다국어 지원 등의 고급 기능을 포함합니다.

    Attributes:
        api_key (str): Google Places API 키
        timeout (float): API 요청 타임아웃 시간 (초)
        client (places_v1.PlacesAsyncClient): 비동기 Places API 클라이언트

    Raises:
        ValueError: GOOGLE_PLACES_API_KEY 환경변수가 설정되지 않은 경우

    Example:
        service = PlacesService(timeout=20.0)
        result = await service.text_search("강남역 카페", "places.displayName", "", "ko")
    """

    def __init__(self, timeout: float = 15.0):
        """
        PlacesService 인스턴스를 초기화합니다.
        환경변수에서 API 키를 가져오고, Google Cloud Client를 설정합니다.

        Args:
            timeout (float, optional): API 요청 타임아웃 시간 (초). 기본값은 15.0초.

        Raises:
            ValueError: GOOGLE_PLACES_API_KEY 환경변수가 설정되지 않은 경우

        Note:
            API 키는 반드시 'GOOGLE_PLACES_API_KEY' 환경변수로 설정되어야 합니다.
        """
        self.api_key: str | None = os.getenv("GOOGLE_PLACES_API_KEY")
        self.timeout: float = timeout

        if not self.api_key:
            raise ValueError(
                "Google Places API 키가 설정되지 않았습니다. "
                "환경변수 'GOOGLE_PLACES_API_KEY'를 설정해주세요.\n"
                "예시: GOOGLE_PLACES_API_KEY=AIza..."
            )

        # 타입 검사기를 위한 명시적 체크
        assert self.api_key is not None  # 타입 검사기를 위한 명시적 체크
        # 클라이언트 옵션 설정 (API key 인증)
        options = client_options.ClientOptions(api_key=self.api_key)

        # Places 클라이언트 초기화
        self.client = places_v1.PlacesAsyncClient(client_options=options)

    async def text_search(
        self, query: str, fields: str, types: str, language_code: str
    ) -> Dict[str, Any]:
        """
        텍스트 쿼리를 사용하여 장소를 검색합니다.

        사용자가 입력한 자연어 텍스트를 바탕으로 관련 장소들을 검색하고,
        지정된 필드와 타입 필터, 언어 설정에 따라 결과를 반환합니다.

        Args:
            query (str): 검색할 장소 텍스트.
                예: "강남역 스타벅스", "서울 맛집", "부산 해수욕장"
            fields (str): 반환할 필드 목록 (fieldMask 형식).
                예: "places.id,places.displayName,places.formattedAddress"
            types (str): 필터링할 장소 타입 (Place Type 코드).
                예: "restaurant", "gas_station", "tourist_attraction"
                빈 문자열인 경우 모든 타입 포함
            language_code (str): 응답 언어 코드 (ISO 639-1).
                예: "ko" (한국어), "en" (영어), "ja" (일본어)
                빈 문자열인 경우 기본 언어 사용

        Returns:
            Dict[str, Any]: 검색 결과를 포함한 딕셔너리
                성공 시: {"places": [장소정보1, 장소정보2, ...]}
                실패 시: {"error": "오류메시지", "query": "검색쿼리"}

        Raises:
            InvalidArgument: 잘못된 요청 파라미터인 경우
            PermissionDenied: API 키가 유효하지 않거나 권한이 없는 경우
            ResourceExhausted: API 호출 한도를 초과한 경우
            GoogleAPIError: 기타 Google API 오류
            Exception: 예상치 못한 오류

        Example:
            >>> service = PlacesService()
            >>> result = await service.text_search(
            ...     query="강남역 카페",
            ...     fields="places.displayName,places.formattedAddress",
            ...     types="cafe",
            ...     language_code="ko"
            ... )
            >>> print(result["places"][0]["display_name"])

        Note:
            - 검색 결과는 관련성(RELEVANCE) 순으로 정렬됩니다
            - 최소 평점은 0.0으로 설정되어 모든 평점의 장소가 포함됩니다
            - 가격 수준은 UNSPECIFIED로 설정되어 모든 가격대가 포함됩니다
        """
        try:
            logger.info(f"장소 검색 요청: {query}")

            # SearchTextRequest 생성 - 빈 문자열 처리 개선
            request_params = {
                "text_query": query,
                "min_rating": 0.0,
                "price_levels": [PriceLevel.PRICE_LEVEL_UNSPECIFIED],
                "rank_preference": SearchTextRequest.RankPreference.RELEVANCE,
                "include_pure_service_area_businesses": False,
            }

            # 빈 문자열이 아닌 경우만 추가
            if language_code:
                request_params["language_code"] = language_code
            if types:
                request_params["included_type"] = types

            request = SearchTextRequest(**request_params)

            # API 호출
            response = await self.client.search_text(
                request=request, metadata=[("x-goog-fieldmask", fields)]
            )

            # 응답을 딕셔너리로 변환
            places_list = []
            for place in response.places:
                # protobuf 객체를 딕셔너리로 변환
                place_dict = places_v1.Place.to_dict(place)
                places_list.append(place_dict)

            if not places_list:
                logger.info(f"검색 결과 없음: {query}")
                return {"error": "검색 결과가 없습니다.", "query": query}

            logger.info(f"검색 성공: {len(places_list)}개 결과")
            return {"places": places_list}

        except InvalidArgument as e:
            logger.error(f"잘못된 요청 파라미터: {e}")
            return {
                "error": "잘못된 요청입니다. 쿼리나 필드를 확인해주세요.",
                "query": query,
            }

        except PermissionDenied as e:
            logger.error(f"권한 거부: {e}")
            return {
                "error": "API 키가 유효하지 않거나 접근 권한이 없습니다.",
                "query": query,
            }

        except ResourceExhausted as e:
            logger.error(f"할당량 초과: {e}")
            return {"error": "API 호출 한도를 초과했습니다.", "query": query}

        except GoogleAPIError as e:
            logger.error(f"Google API 오류: {e}")
            return {"error": f"Google API 오류가 발생했습니다: {e}", "query": query}

        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            return {"error": f"예상치 못한 오류가 발생했습니다: {e}", "query": query}


# 전역 인스턴스를 함수로 지연 로딩
_places_service_instance: PlacesService | None = None


def get_places_service() -> PlacesService:
    """PlacesService 싱글톤 인스턴스를 반환합니다."""
    global _places_service_instance
    if _places_service_instance is None:
        _places_service_instance = PlacesService()
    return _places_service_instance


async def text_search_tool(query: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    에이전트에서 사용하는 텍스트 기반 장소 검색 도구입니다.

    이 함수는 ADK(Agent Development Kit) 도구로 등록되어 에이전트가 사용할 수 있으며,
    tool_context를 통해 이전 에이전트들이 선택한 필드, 타입, 언어 설정을 가져와서
    Places API 검색을 수행합니다.

    Args:
        query (str): 검색할 장소 쿼리. 사용자가 입력한 자연어 텍스트.
            예: "홍대 맛집", "강남 카페", "부산역 근처 호텔"
        tool_context (ToolContext): ADK 도구 컨텍스트 객체.
            에이전트 간 상태 공유 및 검색 기록 저장에 사용됩니다.
            다음 키들을 포함할 수 있습니다:
            - "fields": 이전 에이전트가 선택한 필드 마스크
            - "types": 이전 에이전트가 선택한 장소 타입
            - "language": 이전 에이전트가 선택한 언어 코드

    Returns:
        Dict[str, Any]: PlacesService.text_search()와 동일한 형식의 검색 결과
            성공 시: {"places": [장소정보들]}
            실패 시: {"error": "오류메시지", "query": "검색쿼리"}

    Side Effects:
        - tool_context.state에 검색 기록을 "places_search_history" 키로 저장
        - 각 검색 기록에는 쿼리, 결과, 타임스탬프가 포함됨

    Example:
        >>> # 에이전트 워크플로우에서 사용될 때:
        >>> # 1. fields_selector_agent가 "places.displayName,places.rating" 선택
        >>> # 2. types_selector_agent가 "restaurant" 선택
        >>> # 3. language_selector_agent가 "ko" 선택
        >>> # 4. places_agent가 이 도구를 호출:
        >>> result = await text_search_tool("홍대 맛집", tool_context)
        >>> print(result["places"][0]["display_name"])

    Note:
        - fields가 설정되지 않은 경우 기본 필드 세트를 사용합니다
        - 모든 검색은 기록되어 추후 분석이나 캐싱에 활용할 수 있습니다
        - 이 함수는 에이전트 워크플로우의 마지막 단계에서 실행됩니다
    """
    llm_fields_data = tool_context.state.get("fields", DEFAULT_FIELDS)
    logger.info(f"llm_fields_data: {llm_fields_data}")
    llm_types_data = tool_context.state.get("types")
    logger.info(f"llm_types_data: {llm_types_data}")
    llm_language_code_data = tool_context.state.get("language")
    logger.info(f"llm_language_code_data: {llm_language_code_data}")

    # 지연 로딩된 서비스 사용
    places_service = get_places_service()

    result = await places_service.text_search(
        query=query,
        fields=llm_fields_data,
        types=llm_types_data,
        language_code=llm_language_code_data,
    )

    # 상태에 저장
    if "places_search_history" not in tool_context.state:
        tool_context.state["places_search_history"] = []

    tool_context.state["places_search_history"].append(
        {
            "query": query,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    )

    return result
