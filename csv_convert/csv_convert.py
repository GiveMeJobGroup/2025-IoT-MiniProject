import os
import pandas as pd

sleep = pd.DataFrame(columns = ['ID'] + list(range(1, 102)) + ['D', 'R', 'D+R', 'FS', 'RT'])    # RT는 D+R과 FS 충족 시 남은 수면 시간
address = "csv_convert/data/labels"
path = os.listdir(address) # 데이터 파일 리스트

sleep['ID'] = [id.split('_')[0] for id in path]

for i in range(31):
    file_path = address + "/" + path[i] # 경로

    file = pd.read_csv(file_path, sep=' ', names=['time', 'sleep'], header=None) # 텍스트 파일 csv 형태로 읽어오기
    
    stage = file['sleep'][0] # 수면단계 변화 관찰하기 위한 첫번째 단계
    
    col_index = 1
    countR = 0
    countD = 0   

    for size in range(len(file)):
        if file.loc[size, 'sleep'] == 2:
            file.loc[size, 'sleep'] = 1
    
        s = file['sleep'][size]
        if stage != s:      # 수면단계가 다를 때
            if col_index <= 101:
                sleep.iloc[i, col_index] = stage
                col_index += 1
            stage = s
        if file.loc[size, 'sleep'] == 3:
            countD += 1
        elif file.loc[size, 'sleep'] == 5:
            countR += 1
        
    D = (countD*30)/60
    R = (countR*30)/60
    sleep.loc[i, 'D'] = D
    sleep.loc[i, 'R'] = R

    sum = D + R
    if sum >= 120:
        sleep.loc[i, 'D+R'] = 1
    else:
        sleep.loc[i, 'D+R'] = 0

    t = file['time'][len(file)-1]      # Total time(총 시간(s))
    if t/3600 >= 6:
        sleep.loc[i,'FS'] = 1
    else:
        sleep.loc[i, 'FS'] = 0    

    fullTime = 8 * 3600     # 임시 적정수면시간 8시간 * 3600 (초로 변환)
    if (sleep.loc[i, 'D+R'] == 1) and (sleep.loc[i,'FS'] == 1):
        sleep.loc[i,'RT'] = fullTime - t



print(sleep)

save_path = "csv_convert/sleep_data.csv"
sleep.to_csv(save_path, index=False, encoding='utf-8')  # 한글 깨짐 방지