# 📄 create_tables.py
# 이 파일은 SQLite 데이터베이스에 필요한 테이블을 처음 한 번만 생성하는 용도.

from sqlalchemy import create_engine, inspect
from data.models import Base    # models 파일에서 Base 가져오기

# ✅ SQLite용 데이터베이스 파일 설정
# welfare.db라는 이름의 파일이 현재 디렉토리에 생성됩니다.
engine = create_engine("sqlite:///./welfare.db", echo=True)

# ✅ 모든 테이블 생성 (models.py에 정의된 클래스 기반)
# Base.metadata는 SQLAlchemy에서 테이블 구조를 추적하는 메타 정보입니다.
Base.metadata.create_all(bind=engine)

print("✅ 테이블 생성 완료")

# 인스펙터로 테이블 목록 조회
inspector = inspect(engine)
tables = inspector.get_table_names()

print("✅ 생성된 테이블:", tables)