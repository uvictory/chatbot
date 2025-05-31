from flask import Blueprint, request, jsonify
from forms.form_filler import fill_form_from_user_input

# Blueprint 생성: /fill-form API 담당
form_bp = Blueprint("form", __name__)

@form_bp.route("/fill-form", methods=["POST"])
def fill_form():
    # 사용자 입력 받기
    user_input = request.get_json()

    # 신청서 형식에 맞게 데이터 변환
    filled = fill_form_from_user_input(user_input)

    # 자동 채움된 데이터 반환
    return jsonify({"success": True, "filled_form": filled})
