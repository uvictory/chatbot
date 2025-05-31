# 출산 정책 안내 챗봇 백엔드

🔧 기술 스택
	•	Backend: Python (FastAPI)
	•	AI 모델: OpenAI GPT-3.5 / GPT-4
	•	데이터 처리: JSON 기반 정책 정보 파싱 및 구조화
	•	기능: 출산 정책 질문 응답, 신청서 자동 작성, 대화형 문맥 유지

⸻

## 📁 주요 디렉토리
- `routes/`: 사용자 질문, 후속 질문 등 REST API 라우팅
- `gpt/`: GPT API 호출 로직
- `utils/`: 정책 검색 기능
- data/ : 정책 데이터 삽입 스크립트 및 크롤링 처리 로직
