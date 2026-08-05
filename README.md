# 서울시 출산 정책 안내 챗봇 — 백엔드

서울시·지자체의 출산 정책을 안내하는 GPT 기반 챗봇의 백엔드입니다.
종합설계 프로젝트(서울AI재단 협업)에서 백엔드를 담당했습니다.

## 무엇을 하나
- 정책 데이터를 검색해 GPT 응답의 근거로 주입 — 학습되지 않은 최신 정책도 정확히 안내
- 대화 맥락을 유지하는 질문–응답 흐름과 신청서 자동 작성 지원

## 구조
| 경로 | 역할 |
|---|---|
| `routes/` | 챗봇·정책·신청서 REST 라우트 |
| `policy_api/` | FastAPI 기반 정책 API (models · routers · db) |
| `gpt/gpt_service.py` | GPT 호출·응답 처리 |
| `utils/policy_search.py` | 정책 검색 |
| `forms/form_filler.py` | 신청서 자동 채움 |
| `run_fastapi.py` / `app.py` | FastAPI / Flask 실행 진입점 |

## 실행
```bash
pip install -r requirements.txt
python run_fastapi.py
```

## 참고
- 협업 결과물 기준의 확장 버전(임베딩 기반 검색·응답 캐싱 등)은 팀 저장소에서 관리했습니다.
- 프로젝트 상세: [Portfolio](https://app.notion.com/p/3b1961db1c6d80d8908af2b044c90fd8)
