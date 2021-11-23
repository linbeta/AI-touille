import os
import pyarrow
import os
import google.cloud
from google.cloud import bigquery as bq
import datetime
import pandas as pd
import json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ratatouille-ai-e6daa9d44a92.json"
client = bq.Client()

# dataset_table_id = "ratatouille-ai.recipebot.recipe"
# 測試下Query拿資料
QUERY = (
    'SELECT * FROM ratatouille-ai.recipebot.recipe '
)

# QUERY = "SELECT b.recipe_name FROM `ratatouille-ai.recipebot.recipe_material` as a,\
#     `ratatouille-ai.recipebot.recipe` as b, `ratatouille-ai.recipebot.material` as c\
#           where a.recipe_id=b.id and a.material_id=c.id and c.name='豬肉'"


query_job = client.query(QUERY)  # API request
rows = query_job.result()  # Waits for query to finish

for row in rows:
    print(row)
