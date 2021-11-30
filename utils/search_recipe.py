from random import shuffle
import os
from google.cloud import bigquery as bq
from linebot.models import TextSendMessage

# 這一行是串連到GCP的鑰匙,本地跑ngrok時要開起來，部屬時從container設定環境變數，請註解掉避免噴錯
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/ratatouille-ai-e6daa9d44a92.json"
client = bq.Client()

def use_result_tag_to_query(ingredient_main):
    try:
        QUERY = (
            f"SELECT b.url FROM `ratatouille-ai.test_upload_csv.mvp_recipe` as b where b.ingredient_main = '{ingredient_main}' "
        )
        query_job = client.query(QUERY)
        rows = query_job.result()
        # 把要回傳給user的食譜存成reply_recipe_list
        reply_recipe_list = []

        for row in rows:
            reply_recipe_list.append(row[0])

        # 把搜尋到的食譜們洗牌
        shuffle(reply_recipe_list)
        # 抓洗牌後的的第1個來回傳，讓推薦食譜有點變化
        reply_recipe = reply_recipe_list[0]
        # print(reply_recipe)
        reply_message = TextSendMessage(f"推薦含有「{ingredient_main}」的食譜： {reply_recipe}")
        # print(reply_message)
        # 回傳推薦食譜
        return reply_message
    except:
        reply_message = TextSendMessage("食譜資料庫擴充中，敬請期待未來的AI服務~")
        return reply_message


def multiple_ingredient_query(ingredient_list, ing_num):
    # 先把ingredient_list轉成可用的string一整串
    ingredient_list_str = ", ".join(repr(e) for e in ingredient_list)
    QUERY = (
        f"SELECT distinct b.recipe_name, b.URL, c.name, {ing_num} as user_material_cnt, (select count(x.id) "
        f"FROM `ratatouille-ai.recipebot.recipe_material` x, `ratatouille-ai.recipebot.material` y, "
        f"`ratatouille-ai.recipebot.recipe` z WHERE x.material_id = y.id and x.recipe_id = z.id and trim(y.name) "
        f"in ({ingredient_list_str}) and z.recipe_name = b.recipe_name) as match_cnt, "
        f"(SELECT count(material_id) FROM `ratatouille-ai.recipebot.recipe_material` WHERE recipe_id = b.id) "
        f"as recipe_material_cnt "
        f"FROM `ratatouille-ai.recipebot.recipe_material` as a, `ratatouille-ai.recipebot.recipe` as b, "
        f"`ratatouille-ai.recipebot.material` as c WHERE a.recipe_id = b.id and a.material_id = c.id and "
        f"trim(c.name) in ({ingredient_list_str}) order by match_cnt desc, recipe_material_cnt asc, b.recipe_name "
        f"LIMIT 10;"
    )
    query_job = client.query(QUERY)
    rows = query_job.result()
    # 取前4個食譜做成list
    reply_recipe_list = []
    for row in rows:
        # print(row)
        dish = row[0] + " " + row[1]
        if dish not in reply_recipe_list:
            reply_recipe_list.append(dish)
            # print(dish)
    reply_message = []
    for dish in reply_recipe_list[:4]:
        reply_message.append(TextSendMessage(dish))
    # print(reply_message)
    return reply_message


def multiple_ingredient_search():
    # TODO: 新資料庫新的query方法
    pass



# 測試用的code
# result_tag = "豬肉"
# print(use_result_tag_to_query(result_tag))


# 測試用的code

# ingredient_list = ['洋蔥', '豆腐', '雞胸肉']
# # test = str(ingredient_list)
# test = multiple_ingredient_query(ingredient_list, len(ingredient_list))

