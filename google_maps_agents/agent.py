from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from config import COORDINATOR_CONTENT_CONFIG, COORDINATOR_MODEL_NAME

from prompts import COORDINATOR_INSTRUCTION, GLOBAL_INSTRUCTION
from .sub_agents import places_agent


class CoordinatorAgent(LlmAgent):
    """Google Maps API와 상호작용하는 여러 하위 에이전트들의 작업을 조율하는 최상위 에이전트.

    이 에이전트는 사용자의 자연어 입력을 받아 의도를 파악한 후, '장소 검색',
    '경로 찾기' 등 특정 작업을 수행할 수 있는 가장 적절한 하위 에이전트에게 제어권을
    넘기는 라우터(Router) 역할을 수행합니다.

    주요 책임:
      - 사용자 요청의 의도 분석 및 분류
      - 적절한 하위 에이전트 또는 도구로의 작업 위임
      - 전체 대화 흐름 관리
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
    sub_agents=[places_agent],
    disallow_transfer_to_parent=True,  # 최상위 에이전트이므로 부모로 제어를 넘기지 않습니다.
)
