import os

# OpenAI API 키 (환경변수에서 불러옴)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 사용 모델 설정
GPT_3_5_MODEL = "gpt-3.5-turbo"
GPT_4_MODEL = "gpt-4-0125-preview"

# 정책 데이터베이스 경로 (향후 SQLite 사용 시)
POLICY_DB_PATH = "db/policy_db.sqlite"
