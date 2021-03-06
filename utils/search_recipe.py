from random import shuffle
import os
from google.cloud import bigquery as bq
from linebot.models import TextSendMessage

# 這一行是串連到GCP的鑰匙,本地跑ngrok時要開起來，部屬時從container設定環境變數，請註解掉避免噴錯
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/aitouille-adam.json"
client = bq.Client()


def multiple_ingredient_search(ingredient_list, ing_num, line_user_id):
    ingredient_list_str = ", ".join(repr(e) for e in ingredient_list)

    QUERY = (
        f"SELECT distinct b.id, b.recipe_name, b.URL, {ing_num} as user_material_cnt, "
        f"(select count(x.id) from `aitouille-adam.recipebot.recipe_material` x, `aitouille-adam.recipebot.material` y,"
        f"`aitouille-adam.recipebot.recipe` z "
        f"where x.material_id=y.id and x.recipe_id=z.id  and trim(y.name) in ({ingredient_list_str}) "
        f"and z.id=b.id) as match_cnt, "
        f"(select count(material_id) from `aitouille-adam.recipebot.recipe_material` "
        f"where recipe_id = b.id) as recipe_material_cnt, "
        f"images as recipe_image_url, d.my_like "
        f"FROM `aitouille-adam.recipebot.recipe_material` as a,`aitouille-adam.recipebot.recipe` as b, "
        f"aitouille-adam.recipebot.material as c "
        f"left join (select recipe_id, my_like from aitouille-adam.recipebot.user_recipe where line_user_id='{line_user_id}' ) as d on d.recipe_id = b.id "
        f"WHERE a.recipe_id = b.id and a.material_id = c.id and trim(c.name) in ({ingredient_list_str}) "
        f"order by match_cnt desc, recipe_material_cnt asc,b.recipe_name LIMIT 20;"
    )
    # print(line_user_id + " is making multiple recipe search")
    # print(QUERY)
    query_job = client.query(QUERY)
    rows = query_job.result()
    reply_message = []
    # 取前4個食譜做成list
    top_match_recipe_list = []
    match_cnt_2_recipe_list = []
    single_ing_recipe_list = []

    # 備註: row[0]為recipe_id, row[1]為食譜名稱, row[2]為食譜網址, row[6]為食譜圖片網址, row[7]是否存為最愛
    for row in rows:
        dish = [row[0], row[1], row[2], row[6], row[7]]
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
        if len(top_match_recipe_list) > 9:  # Charles 20211222
            top_match_recipe_list = top_match_recipe_list[:9]
        return top_match_recipe_list

    elif len(top_match_recipe_list) < 9 and len(match_cnt_2_recipe_list) > 0:
        shuffle(match_cnt_2_recipe_list)
        return match_cnt_2_recipe_list

    elif len(match_cnt_2_recipe_list) == 0 and len(single_ing_recipe_list) > 0:
        shuffle(single_ing_recipe_list)
        return single_ing_recipe_list
    # 如果搜尋不到東西，回傳一個空的list，結果只會顯示小密技卡片
    else:
        return []


# 查看我收藏的食譜
def get_cookbook(line_user_id):
    QUERY = (
        f"SELECT distinct r.id, r.recipe_name, r.URL "
        f"FROM `aitouille-adam.recipebot.recipe` as r, `aitouille-adam.recipebot.user_recipe` as ur "
        f"WHERE ur.line_user_id = '{line_user_id}' and r.id = ur.recipe_id and ur.my_like='Y';"
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
        f"SELECT m.name FROM `aitouille-adam.recipebot.material` as m"
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
