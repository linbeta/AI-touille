# 拿labels.txt來做食材的class_list
class_list = []
with open('converted_savedmodel/labels.txt', encoding="utf-8") as f:
    for line in f:
        (key, val) = line.split()
        class_list.append(val)


def get_ingredients(text):
    result = []
    for item in class_list:
        if item in text and (item not in result):
            if "洋蔥" in result:
                pass
            else:
                result.append(item)
        elif item in ["豬肉片", "豬五花", "豬絞肉"] and ("豬" in text) and ("豬肉" not in result):
            result.append("豬肉")
    return result
