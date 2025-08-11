from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from .config import COORDINATOR_CONTENT_CONFIG, COORDINATOR_MODEL_NAME
from .prompts import COORDINATOR_INSTRUCTION, GLOBAL_INSTRUCTION
from .sub_agents.places_agent import geocode_agent, places_sequential_agent


class CoordinatorAgent(LlmAgent):
    """Google Maps API 멀티에이전트 시스템의 최상위 조율 에이전트

    사용자의 자연어 요청을 분석하여 의도를 파악하고, 각 작업에 특화된
    하위 에이전트들에게 적절히 작업을 분배하는 라우터 역할을 수행합니다.

    Attributes:
        name (str): 에이전트 이름
        model (Gemini): 사용하는 언어 모델 인스턴스
        description (str): 에이전트의 역할 설명
        instruction (str): 조율 작업을 위한 특화 지시사항
        global_instruction (str): 모든 에이전트 공통 지시사항
        generate_content_config (dict): 콘텐츠 생성 관련 설정값
    """


# CoordinatorAgent 인스턴스 생성
root_agent: CoordinatorAgent = CoordinatorAgent(
    name="coordinator_agent",
    model=Gemini(model=COORDINATOR_MODEL_NAME),
    description="사용자 요청을 분석하여 적절한 하위 에이전트나 도구에 작업을 분배하는 최상위 에이전트입니다.",
    # prompts.py 파일에서 가져온 변수를 사용합니다.
    instruction=COORDINATOR_INSTRUCTION,
    global_instruction=GLOBAL_INSTRUCTION,
    generate_content_config=COORDINATOR_CONTENT_CONFIG,
    sub_agents=[places_sequential_agent, geocode_agent],
    disallow_transfer_to_parent=True,  # 최상위 에이전트이므로 부모로 제어를 넘기지 않습니다.
)
