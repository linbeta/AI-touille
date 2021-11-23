'''
將
包在Dockerfile裡面, 當部屬上線時 一次性的把labels.txt中的食材名稱, 依序存成一項一項的json檔

step1. for迴圈一行一行偵測存取labels.txt 中的資料
step2. 創建json檔並將存取到的val寫入檔案裡
step3. 研究在Dockerfile裡面怎麼寫 <運行cloud build時一次性生成>

紀錄: 原本Dockerfile中第14行指令為
RUN pip install -r requirements.txt &&\
    pip install gunicorn

RUN pip install -r requirements.txt &&\
    pip install gunicorn &&\
    python3 txt_save_to_jsonfile.py
'''

class_dict = {}
with open('converted_savedmodel/labels.txt', encoding="utf-8") as f:
    for line in f:
        (key, val) = line.split()

        #自動創建json檔案並寫入內容, 先將測試的資料寫入自行創建的test_save_json資料夾裡~~
        with open('line_message_json/'+ val + '.json', 'w', encoding="utf-8") as j:
            j.write('[{"type": "text", "text": ' + f'"{val}"' + '}]')
