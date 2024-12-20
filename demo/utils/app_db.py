import sqlite3
import json
from datetime import datetime, timedelta

def get_data_from_database(days):
    # 连接到SQLite数据库
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()

    # 获取当前日期
    current_date = datetime.now()

    # 日期格式化字符串
    date_format = "%Y-%m-%d"

    # 初始化结果列表
    results = []

    for i in range(days):
        # 计算目标日期
        target_date = current_date - timedelta(days=i)
        target_date_str = target_date.strftime(date_format)

        # 查询某一天的数据
        cursor.execute('''
            SELECT id, food, number, kcal, time 
            FROM user_data
            WHERE DATE(time) = ?
        ''', (target_date_str,))

        # 获取查询结果
        rows = cursor.fetchall()

        # 用于存储当天的数据
        daily_data = []
        daily_kcal_total = 0

        # 遍历查询结果
        for row in rows:
            entry = {
                'food': row[1],
                'weight': row[2],
                'kcal': row[3],
                'time': row[4],
            }
            daily_data.append(entry)
            daily_kcal_total += row[3]  # 累加卡路里

        # 将每日数据和卡路里总和添加到结果列表中
        results.append({
            'date': target_date_str,
            'data': daily_data,
            'total_kcal': daily_kcal_total
        })

    # 关闭数据库连接
    conn.close()

    # 将结果转换为JSON格式
    json_results = json.dumps(results, indent=4, ensure_ascii=False)
    return json_results

if __name__ == '__main__':
    print(get_data_from_database(7))