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
            print(dish)
    reply_message = []
    for dish in reply_recipe_list[:4]:
        reply_message.append(TextSendMessage(dish))
    # print(reply_message)
    return reply_message


# todo: ================== 施工完成80% ======================

def multiple_ingredient_search(ingredient_list, ing_num):
    ingredient_list_str = ", ".join(repr(e) for e in ingredient_list)
    QUERY = (
        f"SELECT distinct b.id, b.recipe_name, b.URL, {ing_num} as user_material_cnt, "
        f"(select count(x.id) from `ratatouille-ai.recipebot.recipe_material` x, `ratatouille-ai.recipebot.material` y,"
        f"`ratatouille-ai.recipebot.recipe` z "
        f"where x.material_id=y.id and x.recipe_id=z.id  and trim(y.name) in ({ingredient_list_str}) "
        f"and z.id=b.id) as match_cnt, "
        f"(select count(material_id) from `ratatouille-ai.recipebot.recipe_material` "
        f"where recipe_id = b.id) as recipe_material_cnt, "
        f"(SELECT images FROM `ratatouille-ai.recipebot.recipe` where a.recipe_id = id ) as recipe_image_url, "
        
        f"FROM `ratatouille-ai.recipebot.recipe_material` as a,`ratatouille-ai.recipebot.recipe` as b, "
        f"ratatouille-ai.recipebot.material as c "
        f"WHERE a.recipe_id = b.id and a.material_id = c.id and trim(c.name) in ({ingredient_list_str}) "
        f"order by match_cnt desc, recipe_material_cnt asc,b.recipe_name LIMIT 20;"
    )

    query_job = client.query(QUERY)
    rows = query_job.result()
    reply_message = []
    # 取前4個食譜做成list
    top_match_recipe_list = []
    match_cnt_2_recipe_list = []
    single_ing_recipe_list = []

    # 備註: row[0]為recipe_id, row[1]為食譜名稱, row[2]為食譜網址, row[6]為食譜圖片網址
    for row in rows:
        dish = [row[0], row[1], row[2], row[6]]
        if row[4] == row[3]:
            top_match_recipe_list.append(dish)
        elif row[4] == row[3] - 1:
            top_match_recipe_list.append(dish)
        elif row[4] == 2:
            match_cnt_2_recipe_list.append(dish)
        elif row[4] == 1:
            # reply_message.append(TextSendMessage("單一食材搜尋食譜如下："))
            single_ing_recipe_list.append(dish)
    if len(top_match_recipe_list) > 3:
        shuffle(top_match_recipe_list)
        # 如果超過4個，只取洗牌後的前4個出來
        if len(top_match_recipe_list) > 4:
            top_match_recipe_list = top_match_recipe_list[:4]
        return top_match_recipe_list

    elif len(top_match_recipe_list) < 4 and len(match_cnt_2_recipe_list) > 0:
        shuffle(match_cnt_2_recipe_list)
        return match_cnt_2_recipe_list

    elif len(match_cnt_2_recipe_list) == 0 and len(single_ing_recipe_list) > 0:
        reply_message.append(TextSendMessage("僅針對單一食材搜尋："))
        shuffle(single_ing_recipe_list)
        return single_ing_recipe_list

    else:
        # 如果查詢的食材找不到食譜，訊息告知食譜資料庫查無資料，敬請期待更新
        reply_message.append(TextSendMessage("食譜資料庫查無資料，敬請期待未來的版本更新！"))


# 查看我收藏的食譜
def get_cookbook(line_user_id):
    QUERY = (
            f"SELECT distinct r.id, r.recipe_name, r.URL "
            f"FROM `ratatouille-ai.recipebot.recipe` as r, `ratatouille-ai.recipebot.user_recipe` as ur "
            f"WHERE ur.line_user_id = '{line_user_id}' and r.id = ur.recipe_id;"
    )
    query_job = client.query(QUERY)
    rows = query_job.result()
    my_favorites = {}
    for i, row in enumerate(rows):
        my_favorites[i] = {'recipe_id': row[0], 'recipe_name': row[1], 'recipe_url': row[2]}
    # print(my_favorites)
    return my_favorites


def get_all_material_names():
    QUERY = (
        f"SELECT m.name FROM `ratatouille-ai.recipebot.material` as m"
    )
    query_job = client.query(QUERY)
    rows = query_job.result()
    # for row in rows:
    #     print(row[0])
    with open("text_files/materials.txt", "w", encoding="utf-8") as f:
        for row in rows:
            f.write(row[0] + "\n")

# 刷新text_files/materials.txt檔案
# get_all_material_names()

# 測試用的code

# ingredient_list = ['鳳梨', '蝦子', '洋蔥']
# '牛肉', '地瓜', '雞蛋'
# test = multiple_ingredient_query(ingredient_list, len(ingredient_list))
# test = multiple_ingredient_search(ingredient_list, len(ingredient_list))
