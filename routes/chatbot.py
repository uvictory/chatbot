from flask import Blueprint, request, jsonify
from gpt.gpt_service import get_chat_response
from utils.policy_search import get_policy_context

# Blueprint 생성: /ask API 담당
chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/ask", methods=["POST"])
def ask_chatbot():
    # 클라이언트에서 JSON 형태로 질문을 받음
    data = request.get_json()
    question = data.get("question", "")

    # 질문과 관련된 정책 요약 문맥을 가져옴
    context = get_policy_context(question)

    # GPT 모델을 이용하여 응답 생성
    answer, model = get_chat_response(question, context)

    # 응답 반환
    return jsonify({
        "model": model,
        "answer": answer
    })
