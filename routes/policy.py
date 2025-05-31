from flask import Blueprint, request, jsonify
from utils.policy_search import search_policy

# Blueprint 생성: /policy/search API 담당
policy_bp = Blueprint("policy", __name__)

@policy_bp.route("/policy/search", methods=["GET"])
def search():
    # 검색 쿼리 추출
    query = request.args.get("q", "")

    # 쿼리에 해당하는 정책 검색
    results = search_policy(query)

    # 검색 결과 반환
    return jsonify(results)
