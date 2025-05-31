from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite 데이터베이스 파일 위치 설정
DATABASE_URL = "sqlite:///./welfare.db"

# SQLAlchemy 엔진 생성 (SQLite의 경우 check_same_thread는 False 설정 필요)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 세션 클래스 생성: 요청마다 세션을 생성해 DB에 접근하게 함
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)