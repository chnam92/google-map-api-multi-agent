"""Google Maps Places API Tools for PlacesAgent using Google Cloud Client Library."""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.adk.tools import ToolContext
from google.api_core import client_options
from google.api_core.exceptions import (
    GoogleAPIError,
    InvalidArgument,
    PermissionDenied,
    ResourceExhausted,
)
from google.maps import places_v1
from google.maps.places_v1.types import Place, PriceLevel, SearchTextRequest

# 로거 설정
logger = logging.getLogger(__name__)


class PlacesService:
    """포괄적인 기능을 제공하는 Google Maps Places API 래퍼 클래스 (Google Cloud Client 사용)."""

    def __init__(
        self, timeout: float = 15.0
    ):
        """Google Cloud Client를 사용한 PlacesService 초기화."""
        self.api_key: str = os.getenv("GOOGLE_PLACES_API_KEY")
        self.timeout: float = timeout

        if not self.api_key:
            raise ValueError(
                "Google Places API 키가 설정되지 않았습니다. "
                "환경변수 'GOOGLE_PLACES_API_KEY'를 설정해주세요.\n"
                "예시: GOOGLE_PLACES_API_KEY=AIza..."
            )

        # 클라이언트 옵션 설정 (API key 인증)
        options = client_options.ClientOptions(api_key=self.api_key)

        # Places 클라이언트 초기화
        self.client = places_v1.PlacesAsyncClient(client_options=options)

    async def text_search(self, query: str, fields: str, types: str, language_code: str) -> Place:
        """
        텍스트 쿼리를 사용하여 장소를 검색합니다.

        Args:
            query: 검색할 장소 텍스트 (예: "강남역 스타벅스")
            fields: 반환할 필드 목록 (fieldMask 형식)

        Returns:
            장소 정보 딕셔너리 또는 에러 정보
        """
        try:
            logger.info(f"장소 검색 요청 (Cloud Client): {query}")

            # SearchTextRequest 생성
            request = SearchTextRequest(
                text_query=query,
                language_code=language_code,
                included_type=types,
                min_rating=0.0,
                price_levels=[PriceLevel.PRICE_LEVEL_UNSPECIFIED],
                rank_preference=SearchTextRequest.RankPreference.RELEVANCE,
                include_pure_service_area_businesses=False,
            )

            # Field mask를 메타데이터로 전달

            fieldMask: str = fields

            # API 호출
            response = await self.client.search_text(
                request=request, metadata=[("x-goog-fieldmask", fieldMask)]
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


# 서비스 인스턴스 생성
places_service = PlacesService()


async def text_search_tool(
    query: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """
    텍스트 쿼리로 장소를 검색하는 도구

    Args:
        query: 검색할 장소 쿼리

    Returns:
        검색된 장소 정보
    """
    llm_fields_data = tool_context.state.get("fields", None)
    logger.info(f"llm_fields_data: {llm_fields_data}")
    llm_types_data = tool_context.state.get("types", "")
    logger.info(f"llm_types_data: {llm_types_data}")
    llm_language_code_data = tool_context.state.get("language", "")
    logger.info(f"llm_language_code_data: {llm_language_code_data}")

    if llm_fields_data is None:
        llm_fields_data = "places.id,places.attributions,places.displayName,places.formattedAddress,places.location"

    result = await places_service.text_search(
        query=query, fields=llm_fields_data, types=llm_types_data, language_code=llm_language_code_data
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
