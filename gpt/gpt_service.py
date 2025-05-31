from typing import Optional

import openai
import httpx
from openai import OpenAI
from pandas.core.window.doc import template_see_also

from config import OPENAI_API_KEY, GPT_3_5_MODEL, GPT_4_MODEL, OPENAI_API_BASE

from dotenv import load_dotenv
import os

from pathlib import Path

# ✅ .env 파일의 경로를 상위 폴더(chatbot 루트)로 명시
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 환경 변수 불러오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI API 키 설정
client = OpenAI(api_key=OPENAI_API_KEY)



# GPT에 메시지 전송 함수
def ask_gpt(user_input: str, context: Optional[str] = None) -> str:
    """
    GPT에게 질문을 전잘하고 응답을 반환,
    context가 있을 경우 system 프로프트로 함께 보냅니다.
    """
    try:
        messages = []

        if context:
            messages.append({"role": "system", "content": f"다음은 정책 요약입니다:\n{context}"})
        messages.append({"role": "user", "content": user_input})

        # 질문 복잡도에 따라 GPT 모델 자동 선택
        user_gpt4 = any(word in user_input for word in ["조건", "차이", "해석"])
        model = GPT_4_MODEL if user_gpt4 else GPT_3_5_MODEL

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[GPT 오류] {e}")
        return "GPT 응답 생성 실패"


def ask_gpt_with_history(history: list, new_question: str) -> str:
    """
    이전 대화 이력(history)와 새 질문을 함께 GPT에게 전달하여 응답을 받는 함수.
    :param history: [{"role": "user"/"assistant", "content": "..."}] 형태의 이력 리스트
    :param new_question: 후속 질문 텍스트
    :return: GPT 응답 텍스트
    """
    try:
        messages = history + [{"role": "user", "content": new_question}]

        response = client.chat.completions.create(
            model=GPT_3_5_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[GPT 오류] {e}")
        return "GPT 응답 생성 실패"



def get_chat_response(user_input: str, context: str):
    """
    질문과 정책 요약을 바탕으로 GPT-3.5 또는 GPT-4를 호출해 답변을 생성함
    """
    # 질문의 복잡성에 따라 GPT-4 사용 여부 결정
    use_gpt4 = any(word in user_input for word in ["조건", "차이", "해석"])
    model = GPT_4_MODEL if use_gpt4 else GPT_3_5_MODEL

    # GPT에게 메시지 전달 및 응답 받기
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": f"다음은 정책 문서 요약입니다:{context}"},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        max_tokens=500
    )

    # 응답 내용과 사용한 모델명 반환
    return response.choices[0].message["content"], model
