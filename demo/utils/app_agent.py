from illufly.chat import ChatOpenAI
from illufly.flow import ReAct
import os

from app_main import base_model
from utils.app_db import get_data_from_database

utils_base_model = os.getenv("BASE_MODEL")

def fitness_guide(gender, age, height, weight, goal, target_weight):
    user_info = [f"我的性别为{gender}",f"年龄为{age}",f"身高为{height}",f"体重为{weight}",
                 f"目标为{goal}至{target_weight}"]
    fitness_planner = ChatOpenAI(model="/gemini/code/MiniCPM-V_2_6_awq_int4",knowledge = user_info)
    user_data_last_week = get_data_from_database(7)

    answer = fitness_planner(f"你是一个健康指导师，现在需要你帮助我分析过去一周的饮食数据，并给出相应饮食建议。\n \
                                    以下是我上一周饮食数据的JSON：{user_data_last_week}\n \
                                    现在，你需要根据用户的信息，给出相应的饮食建议，要求如下：\n \
                                    饮食建议需要包含以下内容：\n \
                                    - 饮食模式是否健康：例如是否有高糖高盐摄入。\
                                    - 餐食计划是否合理：例如三餐是否完备。\
                                    - 目标预测：例如是否能达到设定的 target_weight。\
                                    - 改进建议：例如是否能改进饮食模式，给出相关改进建议")
    return answer



def exercise_guide(gender, age, height, weight, goal, target_weight):
    user_info = [f"我的性别为{gender}", f"年龄为{age}", f"身高为{height}", f"体重为{weight}",
                 f"目标为{goal}至{target_weight}"]
    exercise_planner = ChatOpenAI(model=utils_base_model, knowledge=user_info)
    user_data_last_week = get_data_from_database(7)

    answer = exercise_planner(f"你是一个健康指导师，现在需要你帮助我分析过去一周的饮食数据，并给出相应运动建议。\n \
                                    以下是我上一周饮食数据的JSON：{user_data_last_week}\n \
                                    现在，你需要根据我的信息，结合我的实际情况，给出相应的运动建议，要求如下：\n \
                                    运动建议需要包含以下内容：\n \
                                    - 运动类型：例如骑行，跑步，健走等\
                                    - 各项运动的运动时间：例如30分钟\
                                    - 运动距离：例如5公里，若不能提供距离，则不提供\
                                    - 运动强度：例如低，中，高等 \
                                    请给出至少两个运动类型，并在最后写一段话激励用户坚持运动。")
    return answer

if __name__ == "__main__":
    print(fitness_guide("男", 30, 170, 70, "减重", 65))