# import os
# import pandas as pd

# sleep = pd.DataFrame(columns = ['id'])

# for i in range(1, 32):
#     sleep[i] = 'a'

# path = "C:/Users/Admin/Desktop/data/labels"

# list_ = os.listdir(path)

# a = list()

# for i in range(len(list_)):
#     a.insert(i, list_[i].split('_')[0])

# sleep['id'] = a

# sleep_ = sleep.loc[0]




# a = []

# for i in range(len(list_)):
#     a.insert(i, list_[i].split('_')[0])

# # print(a)


# for i in range(3):

#     address = "C:/Users/Admin/Desktop/data/labels/"
#     plus = list_[i]
#     sum_ = address + plus

#     file_ = pd.read_csv(sum_, sep=' ', names=['time', 'sleep'], header=None)
#     # print(file_['sleep'])
    
#     stage = file_['sleep'][0]
#     col_index =1
    
#     for i in range(len(file_)):
#         s = file_['sleep'][i]
#         if stage != s:
#             sleep.iloc[i, col_index] = stage
#             col_index += 1  # 다음 컬럼으로 이동
            
#             # 먼저저장
#             stage = s

#         # sleep.iloc[i, col_index] = stage

# print(sleep)
import os
import pandas as pd

# 빈 데이터프레임 생성
sleep = pd.DataFrame(columns=['id'] + list(range(1, 35)))  # id 컬럼 + 1~31 컬럼

# 폴더 내 파일 목록 가져오기
path = "C:/Users/Admin/Desktop/data/labels"
list_ = os.listdir(path)

# id 컬럼 채우기
sleep['id'] = [filename.split('_')[0] for filename in list_]

# sleep 값을 저장할 행 인덱스
row_index = 0  

for i in range(31):  # 첫 3개 파일만 처리한다고 가정
    file_path = os.path.join(path, list_[i])

    # 파일 읽기 (공백 기준으로 구분)
    file_ = pd.read_csv(file_path, sep=' ', names=['time', 'sleep'], header=None)

    if file_.empty:
        print(f"⚠️ {file_path} 파일이 비어있음!")
        continue

    stage = file_['sleep'][0]  # 첫 번째 값
    col_index = 1  # 첫 번째 컬럼부터 채우기

    for j in range(len(file_)):  
        s = file_['sleep'][j]
        if stage != s:  # 값이 바뀌면 저장
            if col_index < 32:  # 컬럼 개수 초과 방지
                sleep.iloc[row_index, col_index] = stage
            col_index += 1  # 다음 컬럼으로 이동
            stage = s  # 현재 값 업데이트
    
    # 마지막 값 저장 (누락 방지)
    if col_index < 32:
        sleep.iloc[row_index, col_index] = stage

    row_index += 1  # 다음 행으로 이동

# sleep 데이터프레임 출력
print(sleep)

save_path = "C:/Users/Admin/Desktop/data/sleep_data.csv"  # 저장할 경로 설정
sleep.to_csv(save_path, index=False, encoding='utf-8-sig')  # 한글 깨짐 방지