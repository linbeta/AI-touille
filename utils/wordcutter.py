'''
將影像建模labels轉為結巴分詞辭典，並加入常用語字詞
需!pip install jieba
'''

# 將影像建模labels轉為結巴分詞辭典，存成jieba_dict.txt
with open("jieba_dict.txt", "w") as f2:
    with open("converted_savedmodel/labels.txt", encoding="utf-8") as f1:
        for line in f1:
            (key, val) = line.split()
            f2.write(val + "\n")

# jieba_dict.txt續寫入其他常用語字詞(例外字詞)
with open("jieba_dict.txt", "a",encoding="utf-8") as f:
  f.write("蘿蔔\n菜頭\n")

# 進行結巴分詞
# import jieba
# jieba.load_userdict('jieba_dict.txt')
# text = "我今天買了洋蔥蘿蔔紅蘿蔔地瓜小白菜高麗菜大白菜豬絞肉豬肉羊肉"
# print(jieba.lcut(text))

def sen_cut(text):
    import jieba
    jieba.load_userdict('jieba_dict.txt')
    jieba.lcut(text)

'''
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
'''