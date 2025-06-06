from scipy.spatial.distance import cosine

import json
def cosine_similarity(v1: list[float], v2) -> float:
    """
    두 벡터의 코사인 유사도를 계산.
    """
    if isinstance(v2, str):
        v2 = json.loads(v2)
    return 1 - cosine(v1, v2)
def get_policy_context(query: str) -> str:
    """
    향후 DB 또는 정책 문서 요약에서 질의와 관련된 내용을 불러오는 함수
    현재는 더미 텍스트 반환
    """
    return "예시 정책 문서 내용 요약입니다."

def search_policy(query: str) -> list:
    """
    사용자의 검색어와 관련된 정책을 찾아 리스트 형태로 반환
    현재는 하드코딩된 더미 데이터 반환
    """
    return [{"title": "첫만남이용권", "summary": "200만원 바우처 제공"}]
