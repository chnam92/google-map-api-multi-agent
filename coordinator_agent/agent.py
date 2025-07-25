from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from pydantic import Field

from . import prompts


class CoordinatorAgent(LlmAgent):
    """
    여러 에이전트의 작업을 조율하는 코디네이터 에이전트입니다.
    """

# Gemini 모델 설정
# 모델 이름은 사용 가능한 모델 중 하나로 변경할 수 있습니다.
# 예: 'gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-2.5-pro'

# CoordinatorAgent 인스턴스 생성
coordinator_agent_instance = CoordinatorAgent(
    model=Gemini(model="gemini-1.5-flash-latest"),
    description="사용자 요청을 분석하여 적절한 하위 에이전트나 도구에 작업을 분배하는 최상위 에이전트입니다.",
    # 프롬프트 파일에서 가져온 변수를 사용합니다.
    instruction=prompts.COORDINATOR_INSTRUCTION,
    global_instruction=prompts.GLOBAL_INSTRUCTION,
    # tools=[], # 사용할 도구가 있다면 리스트에 추가합니다.
    disallow_transfer_to_parent=True, # 최상위 에이전트이므로 부모로 제어를 넘기지 않습니다.
)

# 생성된 인스턴스 확인 (선택 사항)
if __name__ == "__main__":
    print("CoordinatorAgent 인스턴스가 성공적으로 생성되었습니다.")
    # Gemini 객체의 model 속성을 직접 출력하도록 수정하면 더 명확합니다.
    print(f"모델: {coordinator_agent_instance.model.model}")
    print(f"지시사항: {coordinator_agent_instance.instruction}")
