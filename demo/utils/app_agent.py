from openai import OpenAI
from utils.app_db import get_data_from_database

# 设置OpenAI API密钥
# openai_api_key = ""

utils_base_model = "qwen-vl-plus"
ali_api_key = "sk-9c60fd0afe2540c9a821dad4fa12d62a"
ali_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"

client = OpenAI(
    api_key = ali_api_key,
    base_url = ali_base_url
    )

def fitness_guide(gender, age, height, weight, goal, target_weight):

    user_info = [f"我的性别为{gender}",f"年龄为{age}",f"身高为{height}",f"体重为{weight}",
                 f"目标为{goal}至{target_weight}"]
    
    user_data_last_week = get_data_from_database(7)

    response_fitness = client.chat.completions.create(
        model = utils_base_model,
        messages=[
            {
                "role": "user",
                "content":f"你是一个健康饮食指导师,现在需要你帮助我分析过去一周的饮食数据,并给出相应饮食建议。\n \
                                    以下是我上一周饮食数据的JSON:{user_data_last_week}\
                                    现在,你需要根据用户的信息为:{user_info},给出相应的饮食建议,要求如下:\n \
                                    饮食建议需要包含以下内容:\
                                    - 饮食模式是否健康:例如是否有高糖高盐摄入。\
                                    - 餐食计划是否合理:例如三餐是否完备。\
                                    - 目标预测:例如是否能达到设定的目标体重。\
                                    - 改进建议:例如是否能改进饮食模式,给出相关改进建议。限制字数在300字以内"
            },
        ]
    )
    return response_fitness.choices[0].message.content

def exercise_guide(gender, age, height, weight, goal, target_weight):

    user_info = [f"我的性别为{gender}", f"年龄为{age}", f"身高为{height}", f"体重为{weight}",
                 f"目标为{goal}至{target_weight}"]
    
    user_data_last_week = get_data_from_database(7)
    response_exercise = client.chat.completions.create(
        model = utils_base_model,
        messages=[
            {
                "role": "user",
                "content":f"你是一个健康运动指导师,现在需要你帮助我分析过去一周的饮食数据,并给出相应运动建议。\n \
                                    以下是我上一周饮食数据的JSON:{user_data_last_week}\n \
                                    现在,你需要根据我的信息:{user_info},结合我的实际情况,给出相应的运动建议,要求如下:\n \
                                    运动建议需要包含以下内容:\n \
                                    - 运动类型:例如骑行,跑步,健走等\
                                    - 各项运动的运动时间:例如30分钟\
                                    - 运动距离:例如5公里,若不能提供距离,则不提供\
                                    - 运动强度:例如低,中,高等 \
                                    请给出至少两个运动类型,并在最后写一段话激励用户坚持运动。限制字数在300字以内"
            },
        ]
    )
    return response_exercise.choices[0].message.content

if __name__ == "__main__":
    print(fitness_guide("男", 30, 170, 70, "减重", 65))