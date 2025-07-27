"""Google Maps Places API Tools for PlacesAgent."""

import os
from typing import Dict, List, Any, Optional, Union

from google.adk.tools import ToolContext
import requests


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

    def text_search(self, query: str, fields: List[str] = None, max_results: int = 20) -> Dict[str, Any]:
        """
        텍스트 쿼리를 사용하여 장소를 검색합니다. (Places API 신규)
        
        Args:
            query: 검색할 장소 텍스트 (예: "강남역 스타벅스")
            fields: 반환할 필드 목록 (기본값: 기본 필드들)
            max_results: 최대 결과 수 (기본값: 20, 최대: 20)
            
        Returns:
            장소 정보 딕셔너리 또는 에러 정보
        """
        if not fields:
            fields = [
                "places.id", 
                "places.displayName", 
                "places.formattedAddress",
                "places.location",
                "places.rating",
                "places.types",
                "places.photos",
                "places.regularOpeningHours"
            ]
            
        # Places API (신규) 엔드포인트
        places_url = "https://places.googleapis.com/v1/places:searchText"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": ",".join(fields)
        }
        
        body = {
            "textQuery": query,
            "maxResultCount": min(max_results, 20),
            "languageCode": "ko"
        }

        try:
            response = requests.post(places_url, headers=headers, json=body)
            response.raise_for_status()
            place_data = response.json()

            if not place_data.get("places"):
                return {"error": "검색 결과가 없습니다.", "query": query}

            # 첫 번째 결과만 반환 (기존 동작과 호환성 유지)
            place_details = place_data["places"][0]
            result = self._format_place_data_new(place_details)
            result["search_query"] = query
            result["total_results"] = len(place_data["places"])
            
            return result

        except requests.exceptions.RequestException as e:
            return {"error": f"장소 검색 중 오류가 발생했습니다: {e}", "query": query}



    def geocode(self, address: str) -> Dict[str, Any]:
        """
        주소를 위도/경도 좌표로 변환합니다.
        
        Args:
            address: 변환할 주소
            
        Returns:
            좌표 정보와 정확한 주소
        """
        geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": self.api_key,
            "language": "ko"
        }

        try:
            response = requests.get(geocoding_url, params=params)
            response.raise_for_status()
            geocoding_data = response.json()

            if not geocoding_data.get("results"):
                return {"error": "주소를 찾을 수 없습니다.", "address": address}

            result = geocoding_data["results"][0]
            location = result["geometry"]["location"]
            
            return {
                "lat": location["lat"],
                "lng": location["lng"],
                "formatted_address": result["formatted_address"],
                "place_id": result.get("place_id"),
                "location_type": result["geometry"]["location_type"],
                "input_address": address
            }

        except requests.exceptions.RequestException as e:
            return {"error": f"지오코딩 중 오류가 발생했습니다: {e}"}

    def reverse_geocode(self, lat: float, lng: float) -> Dict[str, Any]:
        """
        위도/경도 좌표를 주소로 변환합니다.
        
        Args:
            lat: 위도
            lng: 경도
            
        Returns:
            주소 정보
        """
        geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{lat},{lng}",
            "key": self.api_key,
            "language": "ko"
        }

        try:
            response = requests.get(geocoding_url, params=params)
            response.raise_for_status()
            geocoding_data = response.json()

            if not geocoding_data.get("results"):
                return {"error": "해당 좌표의 주소를 찾을 수 없습니다.", "lat": lat, "lng": lng}

            result = geocoding_data["results"][0]
            
            return {
                "formatted_address": result["formatted_address"],
                "place_id": result.get("place_id"),
                "location_type": result["geometry"]["location_type"],
                "address_components": result.get("address_components", []),
                "input_coordinates": {"lat": lat, "lng": lng}
            }

        except requests.exceptions.RequestException as e:
            return {"error": f"역지오코딩 중 오류가 발생했습니다: {e}"}


# 서비스 인스턴스 생성
places_service = PlacesService()


def text_search_tool(query: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    텍스트 쿼리로 장소를 검색하는 도구
    
    Args:
        query: 검색할 장소 텍스트
        tool_context: ADK 도구 컨텍스트
        
    Returns:
        검색된 장소 정보
    """
    result = places_service.text_search(query=query)
    
    # 상태에 저장
    if "places_search_history" not in tool_context.state:
        tool_context.state["places_search_history"] = []
    
    tool_context.state["places_search_history"].append({
        "query": query,
        "result": result,
        "timestamp": __import__("datetime").datetime.now().isoformat()
    })
    
    return result


def nearby_search_tool(lat: float, lng: float, radius: int = 1000, 
                      place_type: str = None, keyword: str = None, 
                      tool_context: ToolContext = None) -> Dict[str, Any]:
    """
    주변 장소 검색 도구
    
    Args:
        lat: 위도
        lng: 경도
        radius: 검색 반경 (미터)
        place_type: 장소 유형
        keyword: 검색 키워드
        tool_context: ADK 도구 컨텍스트
        
    Returns:
        주변 장소 목록
    """
    result = places_service.nearby_search(lat, lng, radius, place_type, keyword)
    
    # 상태에 저장
    if tool_context and "nearby_search_history" not in tool_context.state:
        tool_context.state["nearby_search_history"] = []
    
    if tool_context:
        tool_context.state["nearby_search_history"].append({
            "location": {"lat": lat, "lng": lng},
            "radius": radius,
            "place_type": place_type,
            "keyword": keyword,
            "result": result,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        })
    
    return result



def geocode_tool(address: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    주소를 좌표로 변환하는 도구
    
    Args:
        address: 변환할 주소
        tool_context: ADK 도구 컨텍스트
        
    Returns:
        좌표 정보
    """
    result = places_service.geocode(address)
    
    # 상태에 저장
    if "geocoding_history" not in tool_context.state:
        tool_context.state["geocoding_history"] = []
    
    tool_context.state["geocoding_history"].append({
        "address": address,
        "result": result,
        "timestamp": __import__("datetime").datetime.now().isoformat()
    })
    
    return result


def reverse_geocode_tool(lat: float, lng: float, tool_context: ToolContext) -> Dict[str, Any]:
    """
    좌표를 주소로 변환하는 도구
    
    Args:
        lat: 위도
        lng: 경도
        tool_context: ADK 도구 컨텍스트
        
    Returns:
        주소 정보
    """
    result = places_service.reverse_geocode(lat, lng)
    
    # 상태에 저장
    if "reverse_geocoding_history" not in tool_context.state:
        tool_context.state["reverse_geocoding_history"] = []
    
    tool_context.state["reverse_geocoding_history"].append({
        "coordinates": {"lat": lat, "lng": lng},
        "result": result,
        "timestamp": __import__("datetime").datetime.now().isoformat()
    })
    
    return result 