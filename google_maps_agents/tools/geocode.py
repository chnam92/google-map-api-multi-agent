# google_maps_agents/tools/geocode.py
"""Google Maps Geocoding API Tools for PlacesAgent."""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional
from urllib.parse import quote

import httpx
from google.adk.tools import ToolContext

# 로거 설정
logger = logging.getLogger(__name__)

# 상수 정의
GEOCODING_BASE_URL = "https://geocode.googleapis.com/v4beta/geocode/address"
REVERSE_GEOCODING_BASE_URL = "https://geocode.googleapis.com/v4beta/geocode/location"


class GeocodingService:
    """
    Google Maps Geocoding API를 위한 래퍼 클래스입니다.

    Geocoding 엔드포인트를 사용하며, 주소→좌표(geocode), 좌표→주소(reverse_geocode)를 제공합니다.

    Attributes:
        api_key (str): Google Maps API 키
        latlng (str): 위도/경도 좌표

    Raises:
        ValueError: API 키 환경변수가 설정되지 않은 경우
    """

    def __init__(self, timeout: float = 5.0):
        """
        GeocodingService 인스턴스를 초기화합니다.
        """
        # 두 환경변수 중 하나를 사용 (우선순위: GOOGLE_PLACES_API_KEY > GOOGLE_MAPS_API_KEY)
        self.api_key: Optional[str] = os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv(
            "GOOGLE_MAPS_API_KEY"
        )
        self.timeout: float = timeout

        if not self.api_key:
            raise ValueError(
                "Google Maps API 키가 설정되지 않았습니다. "
                "환경변수 'GOOGLE_PLACES_API_KEY' 또는 'GOOGLE_MAPS_API_KEY'를 설정해주세요. "
                "예시: GOOGLE_MAPS_API_KEY=AIza..."
            )

    async def geocode(self, address: str, language_code: str = "ko") -> Dict[str, Any]:
        """
        주소를 위도/경도 좌표로 변환합니다.

        Args:
            address (str): 변환할 주소
            language_code (str, optional): 언어 코드(예: 'ko').

        Returns:
            Dict[str, Any]: 좌표 및 주소 정보 또는 오류 정보
        """
        # 주소를 URL 경로로 인코딩
        encoded_address = quote(address, safe='')
        url = f"{GEOCODING_BASE_URL}/{encoded_address}"
        
        # 쿼리 파라미터로 API 키와 언어 설정
        params = {"key": self.api_key}
        if language_code:
            params["languageCode"] = language_code

        try:
            logger.info(f"지오코딩 요청: {address}")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
            # v4beta 응답 구조 처리
            logger.info(f"v4beta 응답 데이터: {data}")
            
            results = data.get("results", [])
            if not results:
                return {"error": "주소를 찾을 수 없습니다.", "address": address}

            result = results[0]
            # v4beta 구조: location 직접 참조, formattedAddress 등
            location = result.get("location", {})
            return {
                "lat": location.get("latitude"),
                "lng": location.get("longitude"), 
                "formatted_address": result.get("formattedAddress"),
                "place_id": result.get("placeId"),
                "location_type": result.get("granularity"),  # v4beta에서는 granularity
                "address_components": result.get("addressComponents", []),
                "input_address": address,
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"지오코딩 상태 오류: {e}")
            return {
                "error": f"지오코딩 중 HTTP 상태 오류가 발생했습니다: {e}",
                "address": address,
            }
        except httpx.RequestError as e:
            logger.error(f"지오코딩 요청 실패: {e}")
            return {
                "error": f"지오코딩 중 오류가 발생했습니다: {e}",
                "address": address,
            }
        except Exception as e:
            logger.error(f"지오코딩 예상치 못한 오류: {e}")
            return {
                "error": f"예상치 못한 오류가 발생했습니다: {e}",
                "address": address,
            }

    async def reverse_geocode(
        self, lat: float, lng: float, language_code: str = "ko"
    ) -> Dict[str, Any]:
        """
        위도/경도 좌표를 주소로 변환합니다.

        Args:
            lat (float): 위도
            lng (float): 경도
            language_code (str, optional): 언어 코드(예: 'ko'). 기본값은 Google 기본언어

        Returns:
            Dict[str, Any]: 주소 정보 또는 오류 정보
        """
        # 좌표를 URL 경로로 인코딩
        location_path = f"{lat},{lng}"
        encoded_location = quote(location_path, safe='')
        url = f"{REVERSE_GEOCODING_BASE_URL}/{encoded_location}"
        
        # 쿼리 파라미터로 API 키와 언어 설정
        params = {"key": self.api_key}
        if language_code:
            params["language_code"] = language_code

        try:
            logger.info(f"역지오코딩 요청: lat={lat}, lng={lng}")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            # v4beta 응답 구조 처리
            results = data.get("results", [])
            if not results:
                return {
                    "error": "해당 좌표의 주소를 찾을 수 없습니다.",
                    "lat": lat,
                    "lng": lng,
                }

            result = results[0]
            return {
                "formatted_address": result.get("formattedAddress"),
                "place_id": result.get("placeId"),
                "location_type": result.get("granularity"),
                "address_components": result.get("addressComponents", []),
                "input_coordinates": {"lat": lat, "lng": lng},
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"역지오코딩 상태 오류: {e}")
            return {
                "error": f"역지오코딩 중 HTTP 상태 오류가 발생했습니다: {e}",
                "lat": lat,
                "lng": lng,
            }
        except httpx.RequestError as e:
            logger.error(f"역지오코딩 요청 실패: {e}")
            return {
                "error": f"역지오코딩 중 오류가 발생했습니다: {e}",
                "lat": lat,
                "lng": lng,
            }
        except Exception as e:
            logger.error(f"역지오코딩 예상치 못한 오류: {e}")
            return {
                "error": f"예상치 못한 오류가 발생했습니다: {e}",
                "lat": lat,
                "lng": lng,
            }


# 전역 인스턴스를 함수로 지연 로딩 (싱글톤)
_geocoding_service_instance: Optional[GeocodingService] = None


def get_geocoding_service() -> GeocodingService:
    """GeocodingService 싱글톤 인스턴스를 반환합니다."""
    global _geocoding_service_instance
    if _geocoding_service_instance is None:
        _geocoding_service_instance = GeocodingService()
    return _geocoding_service_instance


async def geocode_tool(address: str, language: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    주소를 좌표로 변환하는 ADK 도구입니다.

    Args:
        address (str): 변환할 주소
        tool_context (ToolContext): ADK 도구 컨텍스트

    Returns:
        Dict[str, Any]: 좌표 및 주소 정보 또는 오류 정보
    """
    logger.info(f"llm_language_code_data: {language}")

    service = get_geocoding_service()
    result = await service.geocode(address=address, language_code=language)

    # 상태에 저장
    if "geocoding_history" not in tool_context.state:
        tool_context.state["geocoding_history"] = []

    tool_context.state["geocoding_history"].append(
        {
            "address": address,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    )

    return result


async def reverse_geocode_tool(
    lat: float, lng: float, language: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """
    좌표를 주소로 변환하는 ADK 도구입니다.

    Args:
        lat (float): 위도
        lng (float): 경도
        tool_context (ToolContext): ADK 도구 컨텍스트

    Returns:
        Dict[str, Any]: 주소 정보 또는 오류 정보
    """
    logger.info(f"llm_language_code_data: {language}")

    service = get_geocoding_service()
    result = await service.reverse_geocode(
        lat=lat, lng=lng, language_code=language
    )

    # 상태에 저장
    if "reverse_geocoding_history" not in tool_context.state:
        tool_context.state["reverse_geocoding_history"] = []

    tool_context.state["reverse_geocoding_history"].append(
        {
            "coordinates": {"lat": lat, "lng": lng},
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    )

    return result
