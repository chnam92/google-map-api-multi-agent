"""
에이전트와 관련된 설정값을 정의하는 파일입니다.
"""

from google.genai import types

# --- 모델 설정 ---
# 모델 이름은 여기서 관리합니다.
# 모델은 Vertex AI 및 LiteLLM에서 사용 가능한 모델 중 하나로 변경할 수 있습니다.
# Ref: 'gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-2.5-pro'
# Ref: https://ai.google.dev/gemini-api/docs/models

COORDINATOR_MODEL_NAME = "gemini-2.5-flash-lite"
FIELDS_SELECTOR_MODEL_NAME = "gemini-2.5-flash-lite"
PARAMETERS_SELECTOR_MODEL_NAME = "gemini-2.5-flash-lite"
PLACES_MODEL_NAME = "gemini-2.5-flash"


# --- 생성 관련 설정 ---
# 낮은 temperature 값은 모델의 응답을 더 일관성 있고 예측 가능하게 만듭니다.
COORDINATOR_CONTENT_CONFIG = types.GenerateContentConfig(
    temperature=0.1,
)

PLACES_CONTENT_CONFIG = types.GenerateContentConfig(
    temperature=0.1,
)
