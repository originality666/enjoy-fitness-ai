import ast
import base64
import json
import re
import sqlite3
from datetime import datetime
import os

import gradio as gr
from openai import OpenAI

from utils.app_agent import fitness_guide, exercise_guide

# 设置OpenAI API密钥
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = os.getenv("OPENAI_API_BASE")
base_model = os.getenv("BASE_MODEL")


client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

# 定义一个函数，用于从Markdown文本中提取JSON
def extract_json_from_markdown(markdown_text):
    # 使用正则表达式找到所有JSON块
    json_pattern = re.compile(r'```json(.*?)```', re.DOTALL)
    matches = json_pattern.findall(markdown_text)

    json_list = []
    for match in matches:
        try:
            json_obj = json.loads(match.strip())
            json_list.append(json_obj)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    return json_list

# 根据食物名称查询其卡路里含量
def query_kcal(name):
    """
    根据食物名称查询其卡路里含量

    该函数通过连接到SQLite数据库来检索特定食物的卡路里信息
    使用LIKE语句在数据库中搜索与给定名称匹配的食物，并返回其卡路里值

    参数:
    name (str): 要查询的食物名称，支持模糊查询

    返回:
    int: 如果找到匹配的食物，则返回其卡路里值；否则返回0
    """
    # 连接到SQLite数据库
    conn = sqlite3.connect('app_data.db')

    # 创建一个游标对象用于执行SQL命令
    cursor = conn.cursor()

    # 执行SQL查询，使用LIKE语句进行模糊匹配食物名称
    cursor.execute("SELECT kcal FROM food_data WHERE name LIKE ?", ('%' + name + '%',))

    # 获取查询结果中的第一条数据
    result = cursor.fetchone()

    # 关闭数据库连接
    conn.close()

    if result:
        return result[0]
    else:
        return -1

    # # 如果找到了匹配的食物，则返回其卡路里值；否则返回0
    # return result[0] if result else 0


def process_json(json_data_list):
    processed_data = []  # 存储处理后的数据

    for json_data in json_data_list:
        for item in json_data:
            name = item.get('name')
            number = item.get('number')  # 这里的number可能是重量
            weight = item.get('weight')

            # 使用 query_kcal(name) 查询卡路里
            kcal_value = query_kcal(name)
            if kcal_value == -1:
                kcal_value = query_kcal(name[1:])

            # 计算 kcal, 保留一位小数
            kcal = round(weight * 0.01 * kcal_value, 1)

            # 获取当前时间
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 将处理后的数据添加到新的数组
            processed_data.append({
                'food': name,
                'number': weight,
                'kcal': kcal,
                'time': current_time
            })

    return processed_data


def extract_list_string_from_text(response_text):
    # 使用正则表达式查找列表的数据部分
    list_pattern = re.compile(r'\[\{.*?\}\]', re.DOTALL)
    match = list_pattern.search(response_text)

    if match:
        # 返回匹配到的列表字符串
        return match.group(0)
    else:
        print("No list data found in the text.")
        return None

def insert_data_to_db(processed_data):
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()

    for data in processed_data:
        # 将处理后的数据插入到 user_data 表中
        cursor.execute('''
            INSERT INTO user_data (food, number, kcal, time) VALUES (?, ?, ?, ?)
        ''', (data['food'], data['number'], data['kcal'], data['time']))

    conn.commit()
    conn.close()

# 用于将JSON数据插入数据库
def process_json_to_db(json_data_list):
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()
    processed_data = []  # 存储处理后的数据

    for json_data in json_data_list:
        for item in json_data:
            name = item.get('name')
            number = item.get('number')
            weight = item.get('weight')

            """
            # 使用query_kcal(name)查询卡路里
            kcal_value = query_kcal(name)
            """
            if query_kcal(name) == -1:
                kcal_value = query_kcal(name[1:])
            else:
                kcal_value = query_kcal(name)

            # 计算kcal,保留一位小数
            kcal = round(weight * 0.01 * kcal_value, 1)

            # 获取当前时间
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 将处理后的数据插入到user_data表中
            cursor.execute('''
                INSERT INTO user_data (food, number, kcal, time) VALUES (?, ?, ?, ?)
            ''', (name, weight, kcal, current_time))

            # 将处理后的数据添加到新的数组
            #number原先为食物数量，现在暂时改成重量
            processed_data.append({
                'food': name,
                'number': weight,
                'kcal': kcal,
                'time': current_time
            })

    conn.commit()
    conn.close()

    return processed_data

# 用于将文本美观输出
def pretty_print(json_data):
    pretty_print_text = ""
    total_kcal = 0
    for item in json_data:
        pretty_print_text += f"{item['food']} {item['number']}g {item['kcal']}Kcal\n"
        total_kcal += item['kcal']
    pretty_print_text += f"共摄入 {total_kcal}Kcal"
    return pretty_print_text

# 定义计算BMI的函数
def calculate_bmi(height, weight):
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    #输出保留一位小数
    return round(bmi, 1)

# 定义计算BMR的函数
def calculate_bmr(gender, age, height, weight):
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    #保留一位小数
    return round(bmr, 1)

# 计算BMI,BMR,热量目标
def calculate_bmi_bmr_target_calorie(gender, age, height, weight, goal):
    bmi = calculate_bmi(height, weight)
    calorie_requirement = 0

    if gender == "男":
        bmr = calculate_bmr("male", age, height, weight)
        if goal == "减重":
            calorie_requirement = (bmr - 500)
        elif goal == "增重":
            calorie_requirement = (bmr + 500)
        else:
            calorie_requirement = bmr
    else:
        bmr = calculate_bmr("female", age, height, weight)
        if goal == "减重":
            calorie_requirement = (bmr - 500)
        elif goal == "增重":
            calorie_requirement = (bmr + 500)
        else:
            calorie_requirement = bmr

    return bmi, bmr, calorie_requirement

# 热量检测
def process_image(image):
    # 打开系统提示文件，读取内容
    with open("prompt/sys_prompt_m1.txt", "r", encoding="utf-8") as f:
        sys_prompt = f.read()

    with open("prompt/sys_prompt_m1_review.txt", "r", encoding="utf-8") as f:
        sys_prompt_review = f.read()

    with open(image, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    response = client.chat.completions.create(
        model=base_model,
        messages=[
            {
                "role": "system",
                "content": sys_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ]
    )
    # json_pattern = r'```json[\s\S]*?```'

    response_text = extract_json_from_markdown(response.choices[0].message.content)
    print(response_text)
    user_review_text = process_json(response_text)
    print(user_review_text)

    #再次校验数据正确性
    review_response = client.chat.completions.create(
        model=base_model,
        messages=[
            {
                "role": "system",
                "content": sys_prompt_review
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": str(user_review_text)
                    }
                ]
            }
        ]
    )
    print(review_response.choices[0].message.content)
    review_text = extract_list_string_from_text(review_response.choices[0].message.content)
    #打印review_text与其数据类型
    print("Review Text:", review_text, type(review_text))

    try:
        # 使用 ast.literal_eval 将字符串转换为 Python 列表
        review_data = ast.literal_eval(review_text)
        print("Converted Review Data:", review_data)

        # 传递解析后的列表给 pretty_print
        pretty_print_text = pretty_print(review_data)
        print(pretty_print_text)

        # 执行数据库插入
        insert_data_to_db(review_data)
        return pretty_print_text

    except (SyntaxError, ValueError) as e:
        print("Error converting string to list:", e)
        return "数据异常，请重试。:("

    # """
    # 输出格式如下所示：
    # [[{'name': '火龙果', 'number': 1, 'weight': 100},
    # {'name': '猕猴桃', 'number': 6, 'weight': 300},
    # {'name': '樱桃', 'number': 3, 'weight': 150}]]
    # """

    # output_text_temp = ('拉面 500克 1500Kcal\n共摄入 1500Kcal')
    # llm_output_text 是一个包含解析后的JSON对象的列表。


# 饮食建议
def get_fitness_guide(gender, age, height, weight, goal, target_weight):
    response = fitness_guide(gender, age, height, weight, goal, target_weight)
    output_text = response
    return output_text

# 运动指导
def get_exercise_guide(gender, age, height, weight, goal, target_weight):
    response = exercise_guide(gender, age, height, weight, goal, target_weight)
    output_text = response
    return output_text

# 使用 HTML 和内联 CSS 来设置描述文本的样式
description_html = """
<div style="text-align: center;">
    <h1>Enjoy Fitness Demo</h1>
    <h3>由多模态模型驱动的健康管理系统</h3>
</div>
"""

# 选项热更新
def update_goal(weight, target_weight):
    if target_weight > weight:
        return "增重"
    elif target_weight < weight:
        return "减重"
    else:
        return "保持"

# 创建Gradio界面
with gr.Blocks() as demo:
    gr.Markdown(description_html)
    image_input = gr.Image(type="filepath", label="上传图片")

    # 创建输入框
    with gr.Row():
        gender_input = gr.Dropdown(choices=["男", "女"], label="性别")
        age_input = gr.Number(label="年龄", value=25, precision=0)
        height_input = gr.Slider(100, 200, label="身高 (cm)", value=170)
        weight_input = gr.Slider(40, 200, label="体重 (kg)", value=70)
        goal_input = gr.Dropdown(choices=["保持","增重","减重"], label="选择目标")
        target_weight_input = gr.Slider(40,200,label="目标体重 (kg)", value=70)

    result_output = gr.Textbox(label="返回结果")

    # 创建按钮并设置点击事件
    btn_method_1 = gr.Button("热量检测")
    btn_method_2 = gr.Button("健康建议")
    btn_method_3 = gr.Button("运动指导")

    btn_method_1.click(
        fn=process_image,
        inputs=image_input,
        outputs=result_output
    )

    btn_method_2.click(
        fn=get_fitness_guide,
        inputs=[gender_input, age_input, height_input, weight_input,goal_input,target_weight_input],
        outputs=result_output
    )

    btn_method_3.click(
        fn=get_exercise_guide,
        inputs=[gender_input, age_input, height_input, weight_input,goal_input,target_weight_input],
        outputs=result_output
    )

    weight_input.change(fn=update_goal, inputs=[weight_input, target_weight_input], outputs=goal_input)
    target_weight_input.change(fn=update_goal, inputs=[weight_input, target_weight_input], outputs=goal_input)

# 启动Gradio应用
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
