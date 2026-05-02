"""
核心功能模块 - 财务记录的增删改查及数据持久化
"""

import json
import os
from utils import DATA_FILE, generate_id, ensure_data_file


# ---------- 底层数据操作 ----------

def load_data():
    """
    从 JSON 文件加载全部数据
    返回:
        dict: {"users": {...}, "records": [...]}
    """
    ensure_data_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    """将数据字典写入 JSON 文件"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_records():
    """获取所有收支记录列表"""
    return load_data().get("records", [])


# ---------- 用户认证 ----------

def check_login(username, password):
    """校验用户名密码，返回 True/False"""
    data = load_data()
    users = data.get("users", {})
    return users.get(username) == password


# ---------- 记录 CRUD ----------

def add_record(record_type, amount, category, date, note=""):
    """
    添加一条收支记录
    参数:
        record_type: 'income' 或 'expense'
        amount:      float 金额
        category:    分类名称
        date:        日期字符串 YYYY-MM-DD
        note:        备注（可选）
    返回:
        int: 新记录的 ID
    """
    data = load_data()
    records = data.get("records", [])
    new_id = generate_id(records)

    record = {
        "id": new_id,
        "type": record_type,
        "amount": round(float(amount), 2),
        "category": category,
        "date": date,
        "note": note
    }

    records.append(record)
    data["records"] = records
    save_data(data)
    return new_id


def delete_record(record_id):
    """
    删除指定 ID 的记录
    返回:
        bool: 是否成功删除
    """
    data = load_data()
    records = data.get("records", [])

    for i, r in enumerate(records):
        if r.get("id") == record_id:
            records.pop(i)
            data["records"] = records
            save_data(data)
            return True
    return False


def update_record(record_id, **kwargs):
    """
    更新指定 ID 的记录
    可更新字段: type, amount, category, date, note
    返回:
        bool: 是否成功更新
    """
    data = load_data()
    records = data.get("records", [])

    for r in records:
        if r.get("id") == record_id:
            for key, value in kwargs.items():
                if key in ("type", "amount", "category", "date", "note"):
                    if key == "amount":
                        r[key] = round(float(value), 2)
                    else:
                        r[key] = value
            data["records"] = records
            save_data(data)
            return True
    return False


def get_record_by_id(record_id):
    """根据 ID 获取单条记录，未找到返回 None"""
    records = get_records()
    for r in records:
        if r.get("id") == record_id:
            return r
    return None


# ---------- 筛选与统计 ----------

def filter_by_month(records, year_month):
    """
    按月份筛选（date 字段以 year_month 开头）
    参数:
        records:    记录列表
        year_month: 字符串如 '2026-04'
    """
    return [r for r in records if r.get("date", "").startswith(year_month)]


def filter_by_category(records, category):
    """按分类名称筛选"""
    return [r for r in records if r.get("category") == category]


def filter_by_type(records, record_type):
    """按收支类型筛选"""
    return [r for r in records if r.get("type") == record_type]


def get_monthly_statistics(year_month):
    """
    获取指定月份的汇总统计
    返回:
        dict: {year_month, total_income, total_expense, balance, count, records}
    """
    records = get_records()
    month_records = filter_by_month(records, year_month)

    total_income = sum(r["amount"] for r in month_records if r["type"] == "income")
    total_expense = sum(r["amount"] for r in month_records if r["type"] == "expense")

    return {
        "year_month": year_month,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "count": len(month_records),
        "records": month_records
    }


def get_category_statistics(record_type=None):
    """
    按分类汇总金额
    参数:
        record_type: 可选，'income' / 'expense'，不传则统计全部
    返回:
        dict: {分类名: 总金额}
    """
    records = get_records()
    if record_type:
        records = filter_by_type(records, record_type)

    stats = {}
    for r in records:
        cat = r["category"]
        stats[cat] = stats.get(cat, 0) + r["amount"]
    return stats


def get_all_months():
    """获取所有包含记录的月份列表（降序）"""
    records = get_records()
    months = set()
    for r in records:
        date_str = r.get("date", "")
        if len(date_str) >= 7:
            months.add(date_str[:7])
    return sorted(months, reverse=True)
