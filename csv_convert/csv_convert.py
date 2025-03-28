import os
import pandas as pd

sleep = pd.DataFrame(columns = ['ID'] + list(range(1, 181)) + ['D', 'R', 'D+R', 'FS'])

address = "csv_convert/data/labels"
path = os.listdir(address) # 데이터 파일 리스트

sleep['ID'] = [id.split('_')[0] for id in path]

for i in range(31):
    file_path = address + "/" + path[i] # 경로

    file = pd.read_csv(file_path, sep=' ', names=['time', 'sleep'], header=None) # 텍스트 파일 csv 형태로 읽어오기
    
    stage = file['sleep'][0] # 수면단계 변화 관찰하기 위한 첫번째 단계
    col_index = 1
    
    for size in range(len(file)):
        s = file['sleep'][size]
        if stage != s:      # 수면단계가 다를 때
            if col_index <= 180:
                sleep.iloc[i, col_index] = stage
                col_index += 1
            stage = s

print(sleep)

# save_path = "csv_convert/sleep_data.csv"
# sleep.to_csv(save_path, index=False, encoding='utf-8')  # 한글 깨짐 방지