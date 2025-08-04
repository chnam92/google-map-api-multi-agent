from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.google_llm import Gemini

from ...config import (FIELDS_SELECTOR_MODEL_NAME, PLACES_CONTENT_CONFIG,
                       PLACES_MODEL_NAME)
from ...prompts import (GLOBAL_INSTRUCTION, PARAMETERS_SELECTOR_INSTRUCTION,
                        PLACES_INSTRUCTION)
from ...tools.places import text_search_tool


class PlacesAgent(LlmAgent):
    """
    CoordinatorAgent로부터 받은 장소 검색 요청을 처리하고,
    Google Maps Places API를 활용한 TextSearch 요청을 처리하는 에이전트입니다.
    사용자가 요청한 위치 주변의 관심 장소(POI)를 찾아
    장소 정보를 제공하는 역할을 담당합니다.


    Attributes:
    name (str): 에이전트 이름 ('places_agent')
    model (Gemini): 사용하는 언어 모델
    description (str): 에이전트 설명
    instruction (str): 에이전트 지시사항
    global_instruction (str): 전역 지시사항
    generate_content_config (dict): 콘텐츠 생성 설정
    """


parameter_selector_agent: PlacesAgent = PlacesAgent(
    name="fields_selector_agent",
    model=Gemini(model=FIELDS_SELECTOR_MODEL_NAME),
    description="TextSearch 요청을 분석하고, 최적의 파라미터를 선택하고 반환하는 에이전트입니다.",
    instruction=PARAMETERS_SELECTOR_INSTRUCTION,
    generate_content_config=PLACES_CONTENT_CONFIG,
    output_key="fields",
)


places_agent: PlacesAgent = PlacesAgent(
    name="places_agent",
    model=Gemini(model=PLACES_MODEL_NAME),
    description="CoordinatorAgent로 부터 받은 장소 검색 요청을 처리하는 에이전트입니다.",
    # prompts.py 파일에서 가져온 변수를 사용합니다.
    instruction=PLACES_INSTRUCTION,
    global_instruction=GLOBAL_INSTRUCTION,
    generate_content_config=PLACES_CONTENT_CONFIG,
    tools=[text_search_tool],
)

places_sequential_agent = SequentialAgent(
    sub_agents=[parameter_selector_agent, places_agent],
    name="places_sequential_agent",
    description="LLM을 사용하여 TextSearch 요청을 처리하기 위해 절차를 가진 에이전트입니다.",
)
