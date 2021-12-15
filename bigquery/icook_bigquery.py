""" 最終版,使用前須先更改要修改的檔案 """

import csv
from random import shuffle
import os
from google.cloud import bigquery as bq
from linebot.models import TextSendMessage
import os
from google.cloud import storage
from google.cloud import bigquery 
import pandas as pd
import requests
from bs4 import BeautifulSoup
#環境變數
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/ratatouille-ai-e6daa9d44a92.json"
client = bq.Client()

QUERY = "SELECT `URL` FROM `ratatouille-ai.recipebot.recipe`" 
job = client.query(QUERY)
result = job.result()
for Row in result:
    print(Row[0])
    if "icook" in Row[0]:
      r1 = requests.get(f'{Row[0]}',
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
            'cookie': 'visitor=13728257989256429706; _pbjs_userid_consent_data=3524755945110770; _gcl_au=1.1.1407276380.1636535883; __auc=1644db7717d0923d5aa8c8a7763; _cc_id=17d75d4dc0c20fd4d2f4d9c602b0a854; dable_uid=64813915.1557747589578; _fbp=fb.1.1636536101280.619772029; truvid_protected={"val":"c","level":2,"geo":"TW","timestamp":1636775067}; most_ga=GA1.2.34690171.1636535883; one_fp=%252213fd4b6d679c436ade61d611fd0d848d%2522; oid=%257B%2522oid%2522%253A%25229b7d9231-7202-11e9-9754-0242ac120003%2522%252C%2522ts%2522%253A1557369113%252C%2522v%2522%253A%252220201117%2522%257D; _ss_pp_id=cca3d3783e3b19abd4895b852b2d4ee7; __gads=ID=96c2766af3d6a92e:T=1636535884:S=ALNI_MYS5el3OR4U5OJhhi0U7TkmdS4oww; CF-IPCountry=TW; __asc=a3f0f64a17da77b60806096ad70; AMP_TOKEN=%24NOT_FOUND; _gid=GA1.2.1747816658.1639192421; panoramaId_expiry=1639797222115; panoramaId=b8c7f4a7f829f3cdc9af2ce7d85916d5393849710059b2547127eb8463273cb7; ucf_uid=d893211d-3f92-47ed-9803-cc5c4ac56e33; sent-cid=1639192421; CSRF-TOKEN=v1erMM3oZQZAKidoQtxKc3LzDa4beX58RW2ezDXhndI5DINVEW1zQPh%2FOXU24CCdJPSIvZ6Q8YL0VTyKyzxS6w%3D%3D; _icook_sess=TkRQeTRHTVdoNmVPT1hPa3ZwRURicnBkQW9LMzVUcElIbE41RWlPcXBLaG16QzRyK05BeVIrMktFeW5ReElrZWN0a0tiRzhvNHAzNTZFNWdadnRTQUhBQkVhOVVMY0Y3V091QXd2M3pWKzloNHVPbm1sTXdtZlF5TGZEcUYwOURWT3VrOXNtNG5kNSswWEpUZHBEQ3B0T1pPQVlNc29Ma0VDN0dTVUdwZ2dMeGpyZVNIcFpRUzBFOTgzR1UxaFoyVUsxalVyZW1HdFF1eHQ4dDYxYXJCQUNyQWJhSWNIYjkvcDBMZjFTQ0F5VmpCTEFmZjNpN2lhQm4xZ1M2M2Fzei0tejJuN2gwQ1ZsZE90TjFSYkpRQllZZz09--f4fa37ba63374558e1954c1fc4d448670d9a04e5; _ga_Q65WJCEHK3=GS1.1.1639192420.36.1.1639192494.60; _ga=GA1.2.34690171.1636535883; _ga_ZKZX6M179R=GS1.1.1639192421.33.1.1639192507.48; _td=91f832d2-dda8-4d75-a8c4-2bfe84a1ed0f'
            })
      soup = BeautifulSoup(r1.text,'html.parser')
      for r in soup.find_all('div',{'class':'recipe-cover'}):
          icook_image = r.find('a').attrs['href']
          #如要插入別的檔案 ratatouille-ai.shane.recipet_to_mvp 需替換此處
          QUERY = f"UPDATE `ratatouille-ai.recipebot.recipe` SET `images`='{icook_image}' WHERE `url`='{Row[0]}'"
          job = client.query(QUERY)
          job.result()

    elif "kikkoman" in Row[0]:
      r1 = requests.get(f'{Row[0]}')
      soup = BeautifulSoup(r1.text,'html.parser')
      for img in soup.find_all('div',{'id':'photo'}): 
          img_src= img.find('img').attrs['src'].split('.') 
          kikkoman_image = "https://www.kikkoman.com.tw" + img_src[1] + ".jpg"
          #如要插入別的檔案 ratatouille-ai.shane.recipet_to_mvp 需替換此處
          QUERY = f"UPDATE `ratatouille-ai.recipebot.recipe` SET `images`='{kikkoman_image}' WHERE `url`='{Row[0]}'"
          job = client.query(QUERY)
          job.result()

print("已成功")