# 필요한 라이브러리 임포트
from sqlalchemy import create_engine
import pandas as pd

# 데이터베이스 연결 정보
host='de30-final-3-db-mysql.cve6gqgcih9t.ap-northeast-2.rds.amazonaws.com'  # RDS 엔드포인트 주소
user = 'admin'      # 사용자 이름
password = '72767276'  # 비밀번호
db = 'de30_final_3'   # 데이터베이스 이름

# SQLAlchemy 엔진 생성
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db}')

# SQL 쿼리
sql_query = """
select * from match_details;
"""

# pandas DataFrame으로 데이터 로드
df = pd.read_sql(sql_query, engine)
print(df.head())  # DataFrame의 첫 몇 행 출력

# map_id별로 데이터의 개수를 계산
map_id_counts = df.groupby('map_id').size().reset_index(name='counts')

# 결과 출력
print(map_id_counts)
