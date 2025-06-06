from openai import OpenAI
import os
from dotenv import load_dotenv

#openai.api_key = os.getenv("OPENAI_API_KEY")
# 상위 디렉토리에 있는 .env 파일 명시적으로 로드
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path)

# 환경변수에서 OPENAI_API_KEY 로드
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

client = OpenAI(api_key=api_key)

def get_embedding(texts: str | list[str], model: str = "text-embedding-3-small") -> list[float] | list[list[float]]:
    """
    주어진 텍스트에 대해 OpenAI의 embedding 벡터로 변환, 배치 처리로 비용 및 속도 최적화
    """
    # 단일 문장이면 리스트로 감싸서 요청
    is_single = isinstance(texts, str)
    input_data = [texts] if is_single else texts

    # OpenAI 임베딩 요청
    response = client.embeddings.create(
        input=texts,
        model=model
    )
    embeddings = [d.embedding for d in response.data]
    return embeddings[0] if is_single else embeddings

def get_single_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """단일 문장을 임베딩하고 결과 벡터를 반환"""
    return get_embedding([text], model=model)[0] # list로 감싸서 보내고, 첫 번째 결과만 꺼냄