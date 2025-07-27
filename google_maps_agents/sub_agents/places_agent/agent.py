from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from config import PLACES_CONTENT_CONFIG, PLACES_MODEL_NAME

from prompts import PLACES_INSTRUCTION, GLOBAL_INSTRUCTION


class PlacesAgent(LlmAgent):
    """
    Google Maps Places API를 활용한 장소 검색 전문 에이전트
    CoordinatorAgent로부터 받은 장소 검색 요청을 처리하고,
    사용자가 요청한 위치 주변의 관심 장소(POI)를 찾아
    상세 정보를 제공하는 역할을 담당합니다.

    Attributes:
    name (str): 에이전트 이름 ('coordinator_agent')
    model (Gemini): 사용하는 언어 모델
    description (str): 에이전트 설명
    instruction (str): 에이전트 지시사항
    global_instruction (str): 전역 지시사항
    generate_content_config (dict): 콘텐츠 생성 설정
    """


# CoordinatorAgent 인스턴스 생성
root_agent: PlacesAgent = PlacesAgent(
    name="coordinator_agent",
    model=Gemini(model=PLACES_MODEL_NAME),
    description="CoordinatorAgent로 부터 받은 장소 검색 요청을 처리하는 에이전트입니다.",
    # prompts.py 파일에서 가져온 변수를 사용합니다.
    instruction=PLACES_INSTRUCTION,
    global_instruction=GLOBAL_INSTRUCTION,
    generate_content_config=PLACES_CONTENT_CONFIG,
    # tools=[], # 사용할 도구가 있다면 리스트에 추가합니다.
)
