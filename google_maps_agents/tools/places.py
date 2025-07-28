"""Google Maps Places API Tools for PlacesAgent."""
import json
import os
from typing import Any, Dict, List

import requests
from google.adk.tools import ToolContext


class PlacesService:
    """Wrapper to Google Maps Places API with comprehensive functionality."""

    def __init__(self):
        """Initialize PlacesService with API key validation."""
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")

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
            max_results: 최대 결과 수 (기본값: 20, 최대: 20)

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

        body = {"textQuery": query, "languageCode": "ko"}

        try:
            response = requests.post(places_url, headers=headers, json=body)
            response.raise_for_status()
            place_data = response.json()

            if not place_data.get("places"):
                return {"error": "검색 결과가 없습니다.", "query": query}

            return place_data

        except requests.exceptions.RequestException as e:
            return {"error": f"장소 검색 중 오류가 발생했습니다: {e}", "query": query}


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
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
    )

    return result
