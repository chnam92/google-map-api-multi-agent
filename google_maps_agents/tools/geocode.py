# def geocode(self, address: str) -> Dict[str, Any]:
#         """
#         주소를 위도/경도 좌표로 변환합니다.

#         Args:
#             address: 변환할 주소

#         Returns:
#             좌표 정보와 정확한 주소
#         """
#         geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
#         params = {"address": address, "key": self.api_key, "language": "ko"}

#         try:
#             response = requests.get(geocoding_url, params=params)
#             response.raise_for_status()
#             geocoding_data = response.json()

#             if not geocoding_data.get("results"):
#                 return {"error": "주소를 찾을 수 없습니다.", "address": address}

#             result = geocoding_data["results"][0]
#             location = result["geometry"]["location"]

#             return {
#                 "lat": location["lat"],
#                 "lng": location["lng"],
#                 "formatted_address": result["formatted_address"],
#                 "place_id": result.get("place_id"),
#                 "location_type": result["geometry"]["location_type"],
#                 "input_address": address,
#             }

#         except requests.exceptions.RequestException as e:
#             return {"error": f"지오코딩 중 오류가 발생했습니다: {e}"}

#     def reverse_geocode(self, lat: float, lng: float) -> Dict[str, Any]:
#         """
#         위도/경도 좌표를 주소로 변환합니다.

#         Args:
#             lat: 위도
#             lng: 경도

#         Returns:
#             주소 정보
#         """
#         geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
#         params = {"latlng": f"{lat},{lng}", "key": self.api_key, "language": "ko"}

#         try:
#             response = requests.get(geocoding_url, params=params)
#             response.raise_for_status()
#             geocoding_data = response.json()

#             if not geocoding_data.get("results"):
#                 return {
#                     "error": "해당 좌표의 주소를 찾을 수 없습니다.",
#                     "lat": lat,
#                     "lng": lng,
#                 }

#             result = geocoding_data["results"][0]

#             return {
#                 "formatted_address": result["formatted_address"],
#                 "place_id": result.get("place_id"),
#                 "location_type": result["geometry"]["location_type"],
#                 "address_components": result.get("address_components", []),
#                 "input_coordinates": {"lat": lat, "lng": lng},
#             }

#         except requests.exceptions.RequestException as e:
#             return {"error": f"역지오코딩 중 오류가 발생했습니다: {e}"}

# def geocode_tool(address: str, tool_context: ToolContext) -> Dict[str, Any]:
#     """
#     주소를 좌표로 변환하는 도구

#     Args:
#         address: 변환할 주소
#         tool_context: ADK 도구 컨텍스트

#     Returns:
#         좌표 정보
#     """
#     result = places_service.geocode(address)

#     # 상태에 저장
#     if "geocoding_history" not in tool_context.state:
#         tool_context.state["geocoding_history"] = []

#     tool_context.state["geocoding_history"].append(
#         {
#             "address": address,
#             "result": result,
#             "timestamp": __import__("datetime").datetime.now().isoformat(),
#         }
#     )

#     return result


# def reverse_geocode_tool(
#     lat: float, lng: float, tool_context: ToolContext
# ) -> Dict[str, Any]:
#     """
#     좌표를 주소로 변환하는 도구

#     Args:
#         lat: 위도
#         lng: 경도
#         tool_context: ADK 도구 컨텍스트

#     Returns:
#         주소 정보
#     """
#     result = places_service.reverse_geocode(lat, lng)

#     # 상태에 저장
#     if "reverse_geocoding_history" not in tool_context.state:
#         tool_context.state["reverse_geocoding_history"] = []

#     tool_context.state["reverse_geocoding_history"].append(
#         {
#             "coordinates": {"lat": lat, "lng": lng},
#             "result": result,
#             "timestamp": __import__("datetime").datetime.now().isoformat(),
#         }
#     )

#     return result
