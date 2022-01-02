import os
from google.cloud import bigquery as bq

# 這一行是串連到GCP的鑰匙,本地跑ngrok時要開起來，部屬時從container設定環境變數，請註解掉避免噴錯
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/aitouille-adam.json"
client = bq.Client()


def remove_recipe_from_cookbook(user_id, recipe_id_int):
    Query = (
        f"Delete `ratatouille-ai.recipebot.user_recipe` "
        f"where recipe_id = {recipe_id_int} and line_user_id = '{user_id}';"
    )
    query_job = client.query(Query)  # API request
    # print(f"{recipe_id_int} removed")
