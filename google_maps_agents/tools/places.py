"""Google Maps Places API Tools for PlacesAgent."""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from google.adk.tools import ToolContext

# 로거 설정
logger = logging.getLogger(__name__)


class PlacesService:
    """포괄적인 기능을 제공하는 Google Maps Places API 래퍼 클래스."""

    def __init__(self, language_code: str = "ko", request_timeout: int = 30):
        """Initialize PlacesService with API key validation."""
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        self.language_code = language_code
        self.request_timeout = request_timeout

        if not self.api_key:
            raise ValueError(
                "Google Places API 키가 설정되지 않았습니다. "
                "환경변수 'GOOGLE_PLACES_API_KEY'를 설정해주세요.\n"
                "예시: GOOGLE_PLACES_API_KEY=AIza..."
            )

    def text_search(self, query: str, fields: str) -> Dict[str, Any]:
        """
        텍스트 쿼리를 사용하여 장소를 검색합니다. (Places API 신규)

        Args:
            query: 검색할 장소 텍스트 (예: "강남역 스타벅스")
            fields: 반환할 필드 목록 (기본값: 기본 필드들)

        Returns:
            장소 정보 딕셔너리 또는 에러 정보
        """

        # Places API (신규) 엔드포인트
        places_url = "https://places.googleapis.com/v1/places:searchText"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": fields,
        }

        body = {"textQuery": query, "languageCode": self.language_code}

        try:
            logger.info(f"장소 검색 요청: {query}")
            response = requests.post(
                places_url, headers=headers, json=body, timeout=self.request_timeout
            )

            # HTTP 상태 코드별 에러 처리
            if response.status_code == 400:
                return {
                    "error": "잘못된 요청입니다. 쿼리나 필드를 확인해주세요.",
                    "query": query,
                }
            elif response.status_code == 401:
                return {"error": "API 키가 유효하지 않습니다.", "query": query}
            elif response.status_code == 403:
                return {
                    "error": "API 접근이 금지되었습니다. 권한을 확인해주세요.",
                    "query": query,
                }
            elif response.status_code == 429:
                return {"error": "API 호출 한도를 초과했습니다.", "query": query}

            response.raise_for_status()
            place_data = response.json()

            if not place_data.get("places"):
                logger.info(f"검색 결과 없음: {query}")
                return {"error": "검색 결과가 없습니다.", "query": query}

            logger.info(f"검색 성공: {len(place_data.get('places', []))}개 결과")
            return place_data

        except requests.exceptions.Timeout:
            logger.error(f"요청 타임아웃: {query}")
            return {"error": "요청 시간이 초과되었습니다.", "query": query}
        except requests.exceptions.ConnectionError:
            logger.error(f"연결 오류: {query}")
            return {"error": "네트워크 연결에 문제가 있습니다.", "query": query}
        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 오류: {e}")
            return {"error": f"장소 검색 중 오류가 발생했습니다: {e}", "query": query}
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            return {"error": f"예상치 못한 오류가 발생했습니다: {e}", "query": query}


# 서비스 인스턴스 생성
places_service = PlacesService()


async def text_search_tool(query: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    텍스트 쿼리로 장소를 검색하는 도구

    Args:
        query: 검색할 장소 텍스트
        tool_context: ADK 도구 컨텍스트

    Returns:
        검색된 장소 정보
    """
    fields_list = tool_context.state.get("fields", "")
    result = places_service.text_search(query=query, fields=fields_list)

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
