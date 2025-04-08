import pymysql
import pandas as pd
import numpy as np

# MySQL 연결 정보
host = 'localhost'
port = 3306
database = 'sleep'
username = 'root'
password = '12345'

# CSV 파일 읽기
csv_file = "csv_convert/sleep_data.csv"
df = pd.read_csv(csv_file)

# 테이블명 설정
table_name = "sleepStage"

try:
    # MySQL 연결
    conn = pymysql.connect(
        host=host,
        user=username,
        passwd=password,
        port=port,
        db=database,
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    # CSV 컬럼명 가져오기
    columns = df.columns

    # 테이블 생성 SQL 작성 
    col_value = []
    for col in columns:
        if col == "id":
            col_value.append(f"`{col}` INTEGER PRIMARY KEY")
        else:
            col_value.append(f"`{col}` INTEGER ")

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        {", ".join(col_value)}
    );
    """
    cursor.execute(create_table_query)

    # # NaN -> None 변환 
    df = df.replace({np.nan: None})

    # insert query
    insert_query = f"""
    INSERT INTO `{table_name}` ({", ".join([f"`{col}`" for col in columns])}) 
    VALUES ({", ".join(['%s'] * len(columns))});
    """
    
    # Query 실행
    for _, row in df.iterrows():
        try:
            cursor.execute(insert_query, tuple(row))

        except Exception as e:
            print(f"데이터 삽입 오류: {e}")
            continue 

    conn.commit()

    print("CSV -> MySQL 완료")

except pymysql.MySQLError as e:
    print(f"MySQL 오류 발생: {e}")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
