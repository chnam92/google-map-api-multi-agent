from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from config import COORDINATOR_CONTENT_CONFIG, COORDINATOR_MODEL_NAME

from prompts import PLACES_INSTRUCTION, GLOBAL_INSTRUCTION


class PlacesAgent(LlmAgent):
    """
    
    """


# CoordinatorAgent 인스턴스 생성
root_agent: PlacesAgent = PlacesAgent(
    name="coordinator_agent",
    model=Gemini(model=COORDINATOR_MODEL_NAME),
    description="사용자 요청을 분석하여 적절한 하위 에이전트나 도구에 작업을 분배하는 최상위 에이전트입니다.",
    # prompts.py 파일에서 가져온 변수를 사용합니다.
    instruction=PLACES_INSTRUCTION,
    global_instruction=GLOBAL_INSTRUCTION,
    generate_content_config=COORDINATOR_CONTENT_CONFIG,
    # tools=[], # 사용할 도구가 있다면 리스트에 추가합니다.
    disallow_transfer_to_parent=True,  # 최상위 에이전트이므로 부모로 제어를 넘기지 않습니다.
)
