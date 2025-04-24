import openai
from config import OPENAI_API_KEY, GPT_3_5_MODEL, GPT_4_MODEL

# OpenAI API 키 설정
openai.api_key = OPENAI_API_KEY

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
