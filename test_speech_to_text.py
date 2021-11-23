'''
step1. audio_serivce那邊會串到此資料夾
step2. 使用GCP Speech-to-text的API
查看看怎麼把 用戶說話->音檔上傳到storage->啟動GCP Speech-to-text->server取翻譯後的值->值回傳給用戶

pip install --upgrade google-cloud-speech
注意喔~~這個每個月超過60分鐘就會開始計費!
'''

'''
待確認: LINE圖文選單那邊要串語音功能??
'''

from google.cloud import speech
speech_client = speech.SpeechClient()
def get_audio_transfor(bucket_name, destination_blob_name):
    gcs_uri = 'gs://' + bucket_name + '/' + destination_blob_name
    print(gcs_uri)
    audio = speech.RecognitionAudio(uri=gcs_uri)

    # 11.23_測試看看本地端的code是否可翻譯
    # import io
    # with io.open('15127146142146.mp3', "rb") as audio_file:
    #     content = audio_file.read()
    # audio = speech.RecognitionAudio(content=content)

    #11.22_config官方文件上的範例, 但噴錯
    # config = speech.RecognitionConfig(
    #     encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    #     sample_rate_hertz=16000,
    #     language_code="en-US",
    # )

    #沒噴錯但抓不到資料
    config = speech.RecognitionConfig(
        {
            "encoding": speech.RecognitionConfig.AudioEncoding.LINEAR16,
            "sample_rate_hertz":16000,
            "language_code":"zh-TW"
        }
    )
    response = speech_client.recognize(config=config, audio=audio)
    print(response)
    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))
        print(result)
