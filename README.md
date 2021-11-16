# 環境設定說明

### 環境變數(Environment Variables)設定

```
LINE_CHANNEL_ACCESS_TOKEN

LINE_CHANNEL_SECRET

USER_INFO_TEMP_BUCKET_NAME：存到 temp_food_image_mvp 這個 bucket

FOOD_IMAGE_BUCKET_NAME：存到 food-image-mvp 這個 bucket
```


### 建立映像檔，設定image路徑與版本號
```
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/ai-touille:0.0.1
```