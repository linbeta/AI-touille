import os
from google.cloud import bigquery as bq
import csv


def insertRecipe(dish_name, dish_url, seasoning, img_url):
    print("dish_name: " + dish_name)
    # print(type(dish_name))
    # print(len(dish_name))

    if len(dish_name) > 0:
        # QUERY = "SELECT count(id) FROM ratatouille-ai.recipebot.recipe where recipe_name='" + dish_name + "'"
        # QUERY = "SELECT id FROM ratatouille-ai.recipebot.recipe where recipe_name='" + dish_name + "' limit 1"
        QUERY = f"SELECT id FROM ratatouille-ai.recipebot.recipe where URL='{dish_url}' limit 1"

        query_job = client.query(QUERY)  # API request
        rows = query_job.result()  # Waits for query to finish

        num_results = rows.total_rows
        print("total_rows: " + str(num_results))

        # for row in rows:
        if num_results == 0:
            # if (row[0]) == 0:
            print("Bingo! Inserting " + dish_name)

            if str(dish_url).find("icook") > 1:
                print("icook")
                publisher_id = 1
            elif str(dish_url).find("ytower") > 1:
                print("ytower")
                publisher_id = 2
            elif str(dish_url).find("cookpad") > 1:
                print("cookpad")
                publisher_id = 3
            elif str(dish_url).find("kikkoman") > 1:
                print("kikkoman")
                publisher_id = 4
            elif str(dish_url).find("cookidoo") > 1:
                print("cookidoo")
                publisher_id = 5
            elif str(dish_url).find("fatnyanya") > 1:
                print("fatnyanya")
                publisher_id = 6
            elif str(dish_url).find("youtube") > 1:
                print("youtube")
                publisher_id = 7
            else:
                publisher_id = 0

            # cur_time=datetime.timestamp(datetime.now())
            # print (cur_time)
            QUERY = (f"insert into ratatouille-ai.recipebot.recipe (id,recipe_name,URL,publisher_id,"
                     f"process_time,complexity,seasoning, images, abstract, created_time,updated_time) "
                     f"values ((select count(id)+1 from ratatouille-ai.recipebot.recipe),'{dish_name}',"
                     f"'{dish_url}',{str(publisher_id)},'30','M','{seasoning}','{img_url}','',"
                     f"(SELECT CURRENT_TIMESTAMP),(SELECT CURRENT_TIMESTAMP))"
                     )
            print (QUERY)
            # QUERY = "insert into ratatouille-ai.recipebot.recipe (id,recipe_name,URL,publisher_id,process_time,complexity,abstract) values ((select count(id)+1 from ratatouille-ai.recipebot.recipe),'"+dish_name+ "','" + dish_url + "',"+ str(publisher_id) +",'30','M','')"

            query_job = client.query(QUERY)  # API request
            rows = query_job.result()  # Waits for query to finish

            QUERY = "select count(id) from ratatouille-ai.recipebot.recipe"
            # print (QUERY)

            query_job = client.query(QUERY)  # API request
            rows = query_job.result()  # Waits for query to finish

            for row in rows:
                r_id = row[0]
                print("count id: " + str(r_id))
            return r_id
        else:
            for row in rows:
                print("Recipe URL found in DB. id: " + str(row[0]))
                r_id = row[0]
            return -1
    else:
        return -2


def insertMaterials(material_string):
    print(material_string)
    # material_string = str(material_string).replace(" ", ",")
    materials = str(material_string).split(",")
    # print (materials)
    material_id = ""

    for i in materials:
        # print (i)
        if i != "":
            QUERY = "SELECT id FROM ratatouille-ai.recipebot.material where name='" + str(i).strip() + "' limit 1"
            # print (QUERY)
            query_job = client.query(QUERY)  # API request
            rows = query_job.result()  # Waits for query to finish

            print(str(rows.total_rows) + " records of " + str(i).strip() + " found in database.")

            if rows.total_rows == 0:
                # print (row)
                # if (row[0]) == 0:
                print("bingo! Inserting " + str(i).strip())
                QUERY = "SELECT count(id)+1 FROM ratatouille-ai.recipebot.material"

                query_job = client.query(QUERY)  # API request
                rows_2 = query_job.result()  # Waits for query to finish
                for row_2 in rows_2:
                    # print (row_2)
                    material_id = material_id + "," + str(row_2[0])

                # QUERY = "Insert into ratatouille-ai.recipebot.material (id, name, status, catagory) values ("+ str(row_2[0]) +",'"+ str(i).strip()+"', 'A', '')"
                QUERY = (f"Insert into ratatouille-ai.recipebot.material (id, name, status, catagory, created_time, updated_time) "
                         f"values ({str(row_2[0])},'{str(i).strip()}', 'A', '',(SELECT CURRENT_TIMESTAMP),(SELECT CURRENT_TIMESTAMP))")

                query_job = client.query(QUERY)  # API request
                rows_2 = query_job.result()  # Waits for query to finish
            elif rows.total_rows >= 0:
                for row in rows:
                    print("Use the material_id found in db: " + str(row[0]))
                    material_id = material_id + "," + str(row[0])
        else:
            print("Empty string detected. Skipped.")

    material_id = material_id.removeprefix(",")
    print("material_id: " + material_id)
    return material_id


def insertRecipeMaterial(recipe_id, material_ids_string):
    material_ids = str(material_ids_string).split(",")

    for i in material_ids:
        print("insert relations: recipe_id: " + str(recipe_id) + " ; material_id: " + str(i))
        QUERY = (f"Insert into ratatouille-ai.recipebot.recipe_material (id, recipe_id, material_id, created_time,updated_time) "
                 f"values ((select count(id)+1 from ratatouille-ai.recipebot.recipe_material),{str(recipe_id)},{i},(SELECT CURRENT_TIMESTAMP),(SELECT CURRENT_TIMESTAMP))")

        query_job = client.query(QUERY)  # API request
        rows = query_job.result()  # Waits for query to finish
    # for i in material_ids:
    #     QUERY = "SELECT count(*) FROM ratatouille-ai.recipebot.recipe_material where recipe_id=" + str(recipe_id)  + " and material_id=" +str(i)

    #     query_job = client.query(QUERY)  # API request
    #     rows = query_job.result()  # Waits for query to finish

    #     if rows.num_results==0:
    #         print("insert relations: recipe_id: "+ str(recipe_id) + " ; material_id: "+ str(i))
    #         QUERY = "Insert into ratatouille-ai.recipebot.recipe_material (id, recipe_id, material_id, created_time,updated_time) values ((select count(id)+1 from ratatouille-ai.recipebot.recipe_material),"+ str(recipe_id) + ","+ i + ",(SELECT CURRENT_TIMESTAMP),(SELECT CURRENT_TIMESTAMP))"

    #         query_job = client.query(QUERY)  # API request
    #         rows = query_job.result()  # Waits for query to finish


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/ratatouille-ai-e6daa9d44a92.json"
client = bq.Client()

with open('recipes_for_import.csv', encoding='utf8') as file:
    reader = csv.reader(file)
    # This skips the first row of the CSV file.
    next(reader)

    for row in reader:
        # print(row)
        stored = str(row[1]).strip()
        # choice = str(row[2]).strip()
        dish_name = str(row[3]).strip()
        dish_url = str(row[4]).strip()
        materials = str(row[5]).strip()
        # seasoning = str(row[5]).strip()
        img_url = str(row[6]).strip()
        seasoning = ""
        if stored == "Y":
            print(dish_name + " is already stored. Skip processing")
        else:
            recipe_id = insertRecipe(dish_name, dish_url, seasoning, img_url)
            print("we get recipe_id: " + str(recipe_id))
            if recipe_id == -1:
                print("Recipe already in DB. Skip processing")
            else:
                print("we get materials: " + materials)
                material_id_string = insertMaterials(materials)
                print("we get material ids: " + material_id_string)
                insertRecipeMaterial(recipe_id, material_id_string)

print("匯入完成！")

# # dataset_table_id = "ratatouille-ai.recipebot.recipe"
# # 測試下Query拿資料
# QUERY = (
#     'SELECT * FROM ratatouille-ai.recipebot.recipe '
# )

# # QUERY = "SELECT b.recipe_name FROM `ratatouille-ai.recipebot.recipe_material` as a,\
# #     `ratatouille-ai.recipebot.recipe` as b, `ratatouille-ai.recipebot.material` as c\
# #           where a.recipe_id=b.id and a.material_id=c.id and c.name='豬肉'"


# query_job = client.query(QUERY)  # API request
# rows = query_job.result()  # Waits for query to finish

# for row in rows:
#     print(row)
