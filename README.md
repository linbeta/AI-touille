# AI-touille 愛廚易

AI-touille 愛廚易 Line Bot AI 機器人讓您可以藉由直接拍照、挑選圖檔或語音，輸入您想烹調的食材的名稱，經過 AI 程式挑選之後(嘿嘿~，電腦不只會挑花生，也會選食譜囉!)，將合適的食譜推薦給您，讓您不用再為煮什麼菜傷透腦筋!!

官網圖文介紹：https://home.ai-touille.fun/

掃描 QR-Code 加好友：

ID: @096oeofl

![img.png](https://github.com/linbeta/AI-touille/blob/main/images%20for%20readme/img.png)


## 版本更新紀錄

```v3.0.3``` 更換影像辨識核心(MobileNetV2)測試

```v3.0.2``` 更換影像辨識核心(DenseNet169)測試

```v3.0.1``` bug fixed, 更換影像辨識核心(EfficientNetB0)測試

```v3.0.0``` 推出一張照片搜尋複數食材的功能，優化推薦食譜呈現版面、搜尋結果不佳時提供小密技引導user嘗試不同操作方式。

```v2.3.1``` 優化收藏食譜/取消食譜的功能

```v2.3.0``` 新增以秘密指令查詢收藏的食譜功能

```v2.2.1``` 優化圖卡呈現，bug fixed

```v2.2.0``` 食譜呈現更新為 carousel template 以圖卡呈現，讓使用者可點選喜歡存到資料庫；優化影像辨識模型，增修2個辨識類別。

```v2.1.0``` 導入 jieba 分詞，擴充語音及文字搜尋可支援的食材；更新影像辨識模型，增加13個辨識類別；食譜擴充，增加300+。

```v2.0.0``` 複數食材搜尋，更新文字處理。

```v1.4.0``` 新增簡易對話語意判別，新增以複數食材搜尋食譜功能，關聯性食譜資料庫上線，食譜資料庫擴充，影像辨識包新增非食材類別。

```v1.3.0``` 新增選擇按鈕，讓user確認辨識度低的照片，擴充食譜資料庫。

```v1.2.0``` 新增語音輸入轉文字功能、辨識度較低食材以文字確認功能，擴充食材辨識種類。

```v1.1.0``` 新增文字搜尋食譜功能，增加食材辨識包&更新食譜。

```v1.0.0``` MVP 拍照辨識食材、推薦食譜。

## 環境設定說明

### 安裝套件  

windows電腦使用以下指令安裝環境
```
pip install -r requirements.txt
```
macOS或是GCP上要是無法操作請用
```
pip3 install -r requirements.txt
```

#### 關於 requirements.txt 文件與安裝套件的注意事項
##### tensorflow-cpu
GCP上運行的套件tensorflow-cpu有指定版本：
```
tensorflow-cpu == 2.4.1
```
本機端或是GCP跑ngrok時如果安裝完套件有跳錯誤碼請手動安裝更新，或是將上面那行的版本號移除。

##### flask_ngrok
如果有出現這個套件的錯誤碼，可以輸入以下指令解決，詳情可以看最底下參考資料中的連結。
```
pip install git+https://github.com/gstaff/flask-ngrok
```

### 環境變數(Environment Variables)設定

GCP Cloud Run 設定 container 資訊時，請點到環境變數的分頁(VARIABLES & SECRETS)設定以下幾個變數：
```
LINE_CHANNEL_ACCESS_TOKEN

LINE_CHANNEL_SECRET

USER_INFO_TEMP_BUCKET_NAME：存到 temp_food_image_mvp 這個 bucket

FOOD_IMAGE_BUCKET_NAME：存到 food-image-mvp 這個 bucket

GOOGLE_APPLICATION_CREDENTIALS: 設定存鑰匙的位置為 keys/ratatouille-ai-e6daa9d44a92.json
```


### 建立映像檔，設定image路徑與版本號

先確認自己是否再對的資料夾(藍字)及GCP專案(黃字Ratatouille-AI)，如果沒有，請用以下指令設定指向GCP專案
```
gcloud config set project [project-id]
```

用docker打包成映像檔，其中 ```--tag``` 後面要接映像檔的名字，更新版本前可以先到GCP cloud run中查看之前更新到哪一版，將版本號往上加。
```
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/ai-touille:0.0.1
```

查看映像檔及版本號路徑如以下截圖所示：

![imag](https://github.com/linbeta/AI-touille/blob/main/images%20for%20readme/cloud_run.png)

![imag](https://github.com/linbeta/AI-touille/blob/main/images%20for%20readme/edit_and_deploy_new_version.png)

![imag](https://github.com/linbeta/AI-touille/blob/main/images%20for%20readme/select.png)

![imag](https://github.com/linbeta/AI-touille/blob/main/images%20for%20readme/check_version.png)



### 在GCP設定環境變數 (跑ngrok時需要用的)

使用Linux的export指令在Terminal輸入指令設定：
```
export LINE_CHANNEL_ACCESS_TOKEN="這邊去LINE後台複製token"

export LINE_CHANNEL_SECRET="貼上要用的secrete"

export USER_INFO_TEMP_BUCKET_NAME="temp_food_image_mvp"

export FOOD_IMAGE_BUCKET_NAME="food-image-mvp"
```

### 連線鑰匙
上傳專案程式碼資料時請勿將 keys 資料夾上傳，專案的.gitignore檔案中有設定不同步keys資料夾，記得如果拉到GCP上面使用時要手動將keys資料夾加進去，我在團隊Google Drive中有放一份，如果需要也可以到GCP中再生一支鑰匙來使用。


### 參考資料
[flask-ngrok GitHub issue: Virtualenv support #2 討論串](https://github.com/gstaff/flask-ngrok/issues/2)


