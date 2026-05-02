"""
工具函数模块 - 提供数据校验、格式化、打印表格等辅助功能
"""

import os
import json
from datetime import datetime


# 数据文件路径（与 utils.py 同目录）
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# 收支类型
RECORD_TYPES = ["income", "expense"]

# 收入分类
INCOME_CATEGORIES = ["工资", "奖金", "投资收益", "兼职", "其他收入"]

# 支出分类
EXPENSE_CATEGORIES = ["餐饮", "交通", "购物", "住房", "娱乐", "医疗", "教育", "其他支出"]

# 类型中文映射
TYPE_CN = {"income": "收入", "expense": "支出"}


def generate_id(records):
    """为记录生成唯一自增ID"""
    if not records:
        return 1
    return max(r.get("id", 0) for r in records) + 1


def validate_amount(amount_str):
    """
    校验金额输入是否合法
    参数:
        amount_str: 用户输入的金额字符串
    返回:
        (bool, float|str) - (是否合法, 转换后的金额或错误信息)
    """
    try:
        amount = float(amount_str)
        if amount <= 0:
            return False, "金额必须大于零"
        if amount > 99999999.99:
            return False, "金额超出合理范围（上限 99999999.99）"
        return True, round(amount, 2)
    except ValueError:
        return False, "金额必须是有效数字，如 100 或 99.99"


def validate_date(date_str):
    """
    校验日期格式是否为 YYYY-MM-DD
    返回:
        (bool, str) - (是否合法, 日期字符串或错误信息)
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, date_str
    except ValueError:
        return False, "日期格式错误，请使用 YYYY-MM-DD 格式（如 2026-04-29）"


def format_currency(amount):
    """将金额格式化为货币显示字符串"""
    return f"¥{amount:,.2f}"


def get_current_date():
    """获取当日日期字符串（YYYY-MM-DD）"""
    return datetime.now().strftime("%Y-%m-%d")


def get_category_choices(record_type):
    """
    根据收支类型返回可选分类列表
    参数:
        record_type: 'income' 或 'expense'
    """
    if record_type == "income":
        return INCOME_CATEGORIES
    else:
        return EXPENSE_CATEGORIES


def print_separator(char="=", length=60):
    """打印分隔线"""
    print(char * length)


def print_record_table(records):
    """
    以对齐表格形式打印记录列表
    参数:
        records: 记录列表
    """
    if not records:
        print("  暂无记录")
        return

    # 表头
    header = f"{'ID':<6}{'类型':<8}{'金额':<12}{'分类':<12}{'日期':<12}{'备注':<16}"
    print_separator("-")
    print(header)
    print_separator("-")

    # 逐行打印
    for r in records:
        rid = r.get("id", "")
        rtype = TYPE_CN.get(r.get("type", ""), r.get("type", ""))
        amount = format_currency(r.get("amount", 0))
        category = r.get("category", "")
        date = r.get("date", "")
        note = r.get("note", "") if r.get("note") else ""
        if len(note) > 15:
            note = note[:14] + "\u2026"  # 截断过长备注

        print(f"{rid:<6}{rtype:<8}{amount:<12}{category:<12}{date:<12}{note:<16}")

    print_separator("-")

    # 汇总行
    total_income = sum(r["amount"] for r in records if r["type"] == "income")
    total_expense = sum(r["amount"] for r in records if r["type"] == "expense")
    print(f"  共 {len(records)} 条 | 收入: {format_currency(total_income)} "
          f"| 支出: {format_currency(total_expense)} "
          f"| 结余: {format_currency(total_income - total_expense)}")
    print_separator("-")


def input_with_cancel(prompt):
    """
    带取消功能的输入函数，输入 q 或 Q 返回 None
    """
    value = input(prompt).strip()
    if value.lower() == "q":
        return None
    return value


def press_enter_to_continue():
    """按回车键返回主菜单"""
    input("\n按 Enter 键返回主菜单...")


def ensure_data_file():
    """
    确保数据文件存在，若不存在则创建包含默认数据的文件
    """
    if not os.path.exists(DATA_FILE):
        default_data = {
            "users": {"admin": "admin123"},
            "records": []
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
