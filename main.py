"""
个人理财记账系统 - 主程序入口
命令行交互式个人财务管理工具
"""

import os
import sys


def _read_password(prompt="  密  码: "):
    """读取密码（本地个人应用，使用明文输入确保兼容性）"""
    return input(prompt).strip()

from utils import (
    validate_amount,
    validate_date,
    get_current_date,
    get_category_choices,
    print_separator,
    print_record_table,
    input_with_cancel,
    press_enter_to_continue,
    TYPE_CN,
    INCOME_CATEGORIES,
    EXPENSE_CATEGORIES
)
from finance import (
    check_login,
    add_record,
    get_records,
    delete_record,
    update_record,
    get_record_by_id,
    filter_by_category,
    get_monthly_statistics,
    get_category_statistics,
    get_all_months
)

# 图表为可选模块，matplotlib 未安装时降级处理
try:
    from chart import generate_pie_chart, generate_bar_chart, generate_monthly_trend
    CHART_AVAILABLE = True
except ImportError:
    CHART_AVAILABLE = False


# ---------- 工具函数 ----------

def clear_screen():
    """清屏"""
    os.system("cls" if os.name == "nt" else "clear")


# ---------- 登录 ----------

def login():
    """
    用户登录流程，最多 3 次尝试
    返回:
        bool: 登录成功返回 True
    """
    print_separator()
    print("       个人理财记账系统")
    print_separator()
    print("\n  请登录系统（默认账号: admin，密码: admin123）\n")

    for attempt in range(3):
        username = input("  用户名: ").strip()
        password = _read_password()

        if check_login(username, password):
            print(f"\n  登录成功，欢迎 {username}！")
            press_enter_to_continue()
            return True
        else:
            remaining = 2 - attempt
            if remaining > 0:
                print(f"  用户名或密码错误，还剩 {remaining} 次机会\n")
            else:
                print("  登录失败次数过多，程序退出")
    return False


# ---------- 菜单功能 ----------

def menu_add_record():
    """添加收支记录"""
    clear_screen()
    print_separator("=")
    print("  添加记录")
    print_separator("=")

    # 1. 选择收支类型
    print("\n  请选择记录类型:")
    print("    1. 收入")
    print("    2. 支出")
    print("    q. 返回")

    choice = input("\n  请输入: ").strip()
    if choice == "1":
        record_type = "income"
    elif choice == "2":
        record_type = "expense"
    else:
        return

    # 2. 选择分类
    categories = get_category_choices(record_type)
    type_cn = TYPE_CN[record_type]
    print(f"\n  请选择{type_cn}分类:")
    for i, cat in enumerate(categories, 1):
        print(f"    {i}. {cat}")

    cat_choice = input_with_cancel("\n  请输入分类编号 (q 取消): ")
    if cat_choice is None:
        return
    try:
        cat_idx = int(cat_choice) - 1
        if cat_idx < 0 or cat_idx >= len(categories):
            print("  分类编号无效")
            press_enter_to_continue()
            return
        category = categories[cat_idx]
    except ValueError:
        print("  输入无效，请输入数字编号")
        press_enter_to_continue()
        return

    # 3. 输入金额
    while True:
        amount_str = input_with_cancel(f"\n  请输入{type_cn}金额 (q 取消): ")
        if amount_str is None:
            return
        valid, result = validate_amount(amount_str)
        if valid:
            amount = result
            break
        print(f"  {result}，请重新输入")

    # 4. 输入日期
    today = get_current_date()
    prompt = f"\n  请输入日期 YYYY-MM-DD（直接回车使用今天 {today}，q 取消）: "
    date_str = input_with_cancel(prompt)
    if date_str is None:
        return
    if date_str == "":
        date = today
    else:
        valid, result = validate_date(date_str)
        if not valid:
            print(f"  {result}")
            press_enter_to_continue()
            return
        date = result

    # 5. 输入备注
    note = input_with_cancel("\n  请输入备注（可选，直接回车跳过，q 取消）: ")
    if note is None:
        return

    # 6. 保存
    record_id = add_record(record_type, amount, category, date, note)
    print(f"\n  记录添加成功！记录 ID: {record_id}")
    press_enter_to_continue()


def menu_view_records():
    """查看所有记录"""
    clear_screen()
    print_separator("=")
    print("  查看所有记录")
    print_separator("=")

    records = get_records()
    if not records:
        print("\n  暂无任何记录，请先添加")
    else:
        print(f"\n  共 {len(records)} 条记录:\n")
        records.sort(key=lambda r: r.get("date", ""), reverse=True)
        print_record_table(records)

    press_enter_to_continue()


def menu_filter_by_month():
    """按月份筛选并统计"""
    clear_screen()
    print_separator("=")
    print("  按月份筛选统计")
    print_separator("=")

    months = get_all_months()
    if not months:
        print("\n  暂无记录，请先添加")
        press_enter_to_continue()
        return

    print("\n  已有记录的月份:")
    for i, m in enumerate(months, 1):
        stats = get_monthly_statistics(m)
        print(f"    {i}. {m}  收入: ¥{stats['total_income']:,.2f}  "
              f"支出: ¥{stats['total_expense']:,.2f}  "
              f"记录: {stats['count']} 条")

    choice = input_with_cancel("\n  请输入月份编号查看详情 (q 取消): ")
    if choice is None:
        return

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(months):
            print("  编号无效")
            press_enter_to_continue()
            return
        year_month = months[idx]
    except ValueError:
        print("  输入无效")
        press_enter_to_continue()
        return

    stats = get_monthly_statistics(year_month)
    clear_screen()
    print_separator("=")
    print(f"  {year_month} 月份统计")
    print_separator("=")
    print(f"\n  总收入: ¥{stats['total_income']:,.2f}")
    print(f"  总支出: ¥{stats['total_expense']:,.2f}")
    print(f"  结  余: ¥{stats['balance']:,.2f}")
    print(f"  记录数: {stats['count']} 条")

    if stats["records"]:
        print()
        stats["records"].sort(key=lambda r: r.get("date", ""), reverse=True)
        print_record_table(stats["records"])

    press_enter_to_continue()


def menu_filter_by_category():
    """按分类筛选记录"""
    clear_screen()
    print_separator("=")
    print("  按分类筛选统计")
    print_separator("=")

    all_cats = INCOME_CATEGORIES + EXPENSE_CATEGORIES
    print("\n  所有分类:")
    print("  ── 收入 ──")
    for i, cat in enumerate(INCOME_CATEGORIES, 1):
        print(f"    {i}. {cat}")
    print("  ── 支出 ──")
    offset = len(INCOME_CATEGORIES)
    for i, cat in enumerate(EXPENSE_CATEGORIES, 1):
        print(f"    {offset + i}. {cat}")

    choice = input_with_cancel("\n  请输入分类编号 (q 取消): ")
    if choice is None:
        return

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(all_cats):
            print("  编号无效")
            press_enter_to_continue()
            return
        category = all_cats[idx]
    except ValueError:
        print("  输入无效")
        press_enter_to_continue()
        return

    records = get_records()
    filtered = filter_by_category(records, category)

    clear_screen()
    print_separator("=")
    print(f"  分类筛选: {category}")
    print_separator("=")

    if not filtered:
        print(f"\n  没有找到分类为「{category}」的记录")
    else:
        total = sum(r["amount"] for r in filtered)
        print(f"\n  共 {len(filtered)} 条记录，合计: ¥{total:,.2f}\n")
        filtered.sort(key=lambda r: r.get("date", ""), reverse=True)
        print_record_table(filtered)

    press_enter_to_continue()


def menu_modify_record():
    """修改已有记录"""
    clear_screen()
    print_separator("=")
    print("  修改记录")
    print_separator("=")

    records = get_records()
    if not records:
        print("\n  暂无记录可修改")
        press_enter_to_continue()
        return

    records.sort(key=lambda r: r.get("date", ""), reverse=True)
    print_record_table(records)

    choice = input_with_cancel("\n  请输入要修改的记录 ID (q 取消): ")
    if choice is None:
        return

    try:
        record_id = int(choice)
    except ValueError:
        print("  输入无效")
        press_enter_to_continue()
        return

    record = get_record_by_id(record_id)
    if not record:
        print(f"  未找到 ID 为 {record_id} 的记录")
        press_enter_to_continue()
        return

    # 展示当前记录
    print(f"\n  当前记录:")
    print(f"    类型: {TYPE_CN.get(record['type'], record['type'])}")
    print(f"    分类: {record['category']}")
    print(f"    金额: ¥{record['amount']:,.2f}")
    print(f"    日期: {record['date']}")
    print(f"    备注: {record.get('note') or '无'}")

    print("\n  请选择要修改的字段（输入字段编号，直接回车保留原值）:")

    # 类型
    new_type = record["type"]
    type_choice = input_with_cancel(
        f"  1. 类型 [当前: {TYPE_CN.get(record['type'], record['type'])}]  输入 1=收入 2=支出 (回车跳过): "
    )
    if type_choice is None:
        return
    if type_choice == "1":
        new_type = "income"
    elif type_choice == "2":
        new_type = "expense"

    # 分类
    categories = get_category_choices(new_type)
    print(f"  2. 分类 [当前: {record['category']}]")
    for i, cat in enumerate(categories, 1):
        print(f"       {i}. {cat}")
    new_category = record["category"]
    cat_choice = input_with_cancel("     请输入编号 (回车跳过): ")
    if cat_choice is None:
        return
    if cat_choice:
        try:
            cat_idx = int(cat_choice) - 1
            if 0 <= cat_idx < len(categories):
                new_category = categories[cat_idx]
            else:
                print(f"      编号超出范围，保持原分类")
        except ValueError:
            print(f"      输入无效，保持原分类")

    # 金额
    new_amount = record["amount"]
    amt_str = input_with_cancel(
        f"  3. 金额 [当前: ¥{record['amount']:,.2f}]  输入新金额 (回车跳过): "
    )
    if amt_str is None:
        return
    if amt_str:
        valid, result = validate_amount(amt_str)
        if valid:
            new_amount = result
        else:
            print(f"      {result}，保持原金额")

    # 日期
    new_date = record["date"]
    date_str = input_with_cancel(
        f"  4. 日期 [当前: {record['date']}]  输入新日期 YYYY-MM-DD (回车跳过): "
    )
    if date_str is None:
        return
    if date_str:
        valid, result = validate_date(date_str)
        if valid:
            new_date = result
        else:
            print(f"      {result}，保持原日期")

    # 备注
    new_note = record.get("note", "")
    note_str = input_with_cancel(
        f"  5. 备注 [当前: {new_note or '无'}]  输入新备注 (回车跳过): "
    )
    if note_str is None:
        return
    if note_str:
        new_note = note_str

    # 执行更新
    update_record(
        record_id,
        type=new_type,
        category=new_category,
        amount=new_amount,
        date=new_date,
        note=new_note
    )
    print(f"\n  记录 {record_id} 已更新")
    press_enter_to_continue()


def menu_delete_record():
    """删除记录"""
    clear_screen()
    print_separator("=")
    print("  删除记录")
    print_separator("=")

    records = get_records()
    if not records:
        print("\n  暂无记录可删除")
        press_enter_to_continue()
        return

    records.sort(key=lambda r: r.get("date", ""), reverse=True)
    print_record_table(records)

    choice = input_with_cancel("\n  请输入要删除的记录 ID (q 取消): ")
    if choice is None:
        return

    try:
        record_id = int(choice)
    except ValueError:
        print("  输入无效")
        press_enter_to_continue()
        return

    record = get_record_by_id(record_id)
    if not record:
        print(f"  未找到 ID 为 {record_id} 的记录")
        press_enter_to_continue()
        return

    # 二次确认
    print(f"\n  确认删除以下记录？")
    print(f"    类型: {TYPE_CN.get(record['type'], record['type'])}  "
          f"金额: ¥{record['amount']:,.2f}  "
          f"分类: {record['category']}  "
          f"日期: {record['date']}")
    confirm = input_with_cancel("\n  输入 y 确认删除，其他键取消: ")
    if confirm and confirm.lower() == "y":
        delete_record(record_id)
        print(f"\n  记录 {record_id} 已删除")
    else:
        print("\n  已取消删除")

    press_enter_to_continue()


def menu_statistics():
    """财务统计概览"""
    clear_screen()
    print_separator("=")
    print("  财务统计概览")
    print_separator("=")

    records = get_records()
    if not records:
        print("\n  暂无记录，请先添加")
        press_enter_to_continue()
        return

    total_income = sum(r["amount"] for r in records if r["type"] == "income")
    total_expense = sum(r["amount"] for r in records if r["type"] == "expense")

    print(f"\n  累计收入: ¥{total_income:,.2f}")
    print(f"  累计支出: ¥{total_expense:,.2f}")
    print(f"  累计结余: ¥{total_income - total_expense:,.2f}")
    print(f"  总记录数: {len(records)} 条")

    # 收入分类统计（带简易柱状图）
    income_stats = get_category_statistics("income")
    if income_stats:
        max_inc = max(income_stats.values())
        print(f"\n  {'─' * 44}")
        print("  收入分类统计:")
        for cat, amt in sorted(income_stats.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(amt / max_inc * 20) if max_inc > 0 else ""
            print(f"    {cat:<8}  ¥{amt:>10,.2f}  {bar}")
    else:
        print("\n  暂无收入记录")

    # 支出分类统计（带简易柱状图）
    expense_stats = get_category_statistics("expense")
    if expense_stats:
        max_exp = max(expense_stats.values())
        print(f"\n  {'─' * 44}")
        print("  支出分类统计:")
        for cat, amt in sorted(expense_stats.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(amt / max_exp * 20) if max_exp > 0 else ""
            print(f"    {cat:<8}  ¥{amt:>10,.2f}  {bar}")
    else:
        print("\n  暂无支出记录")

    press_enter_to_continue()


def menu_charts():
    """图表绘制子菜单"""
    if not CHART_AVAILABLE:
        print("\n  图表模块不可用，请安装 matplotlib: pip install matplotlib")
        press_enter_to_continue()
        return

    while True:
        clear_screen()
        print_separator("=")
        print("  图表绘制")
        print_separator("=")
        print("\n  1. 支出分类饼图（全部）")
        print("  2. 收入分类饼图（全部）")
        print("  3. 支出分类饼图（按月份）")
        print("  4. 收支分类柱状图（全部）")
        print("  5. 收支分类柱状图（按月份）")
        print("  6. 月度收支趋势折线图")
        print("  7. 返回主菜单")
        print_separator("-")

        choice = input("\n  请输入选项: ").strip()

        if choice == "1":
            print("\n  正在生成图表，请在弹出的窗口中查看...")
            generate_pie_chart("expense")
        elif choice == "2":
            print("\n  正在生成图表，请在弹出的窗口中查看...")
            generate_pie_chart("income")
        elif choice == "3":
            months = get_all_months()
            if not months:
                print("\n  暂无记录")
                press_enter_to_continue()
                continue
            print("\n  可选月份:")
            for i, m in enumerate(months, 1):
                print(f"    {i}. {m}")
            m_choice = input_with_cancel("\n  请选择月份 (q 取消): ")
            if m_choice is None:
                continue
            try:
                ym = months[int(m_choice) - 1]
            except (ValueError, IndexError):
                print("  无效选择")
                press_enter_to_continue()
                continue
            print(f"\n  正在生成 {ym} 月份支出饼图，请在弹出的窗口中查看...")
            generate_pie_chart("expense", ym)
        elif choice == "4":
            print("\n  正在生成图表，请在弹出的窗口中查看...")
            generate_bar_chart()
        elif choice == "5":
            months = get_all_months()
            if not months:
                print("\n  暂无记录")
                press_enter_to_continue()
                continue
            print("\n  可选月份:")
            for i, m in enumerate(months, 1):
                print(f"    {i}. {m}")
            m_choice = input_with_cancel("\n  请选择月份 (q 取消): ")
            if m_choice is None:
                continue
            try:
                ym = months[int(m_choice) - 1]
            except (ValueError, IndexError):
                print("  无效选择")
                press_enter_to_continue()
                continue
            print(f"\n  正在生成 {ym} 月份柱状图，请在弹出的窗口中查看...")
            generate_bar_chart(ym)
        elif choice == "6":
            print("\n  正在生成趋势图，请在弹出的窗口中查看...")
            generate_monthly_trend()
        elif choice == "7":
            break
        else:
            print("  无效选项")
            press_enter_to_continue()


# ---------- 主菜单 ----------

def main_menu():
    """主菜单循环"""
    while True:
        clear_screen()
        print_separator("=")
        print("  个人理财记账系统 - 主菜单")
        print_separator("=")
        print("\n  1. 添加收支记录")
        print("  2. 查看所有记录")
        print("  3. 按月份筛选统计")
        print("  4. 按分类筛选统计")
        print("  5. 修改记录")
        print("  6. 删除记录")
        print("  7. 财务统计概览")
        print("  8. 图表绘制")
        print("  0. 退出系统")
        print_separator("-")

        choice = input("\n  请输入选项: ").strip()

        if choice == "1":
            menu_add_record()
        elif choice == "2":
            menu_view_records()
        elif choice == "3":
            menu_filter_by_month()
        elif choice == "4":
            menu_filter_by_category()
        elif choice == "5":
            menu_modify_record()
        elif choice == "6":
            menu_delete_record()
        elif choice == "7":
            menu_statistics()
        elif choice == "8":
            menu_charts()
        elif choice == "0":
            print("\n  感谢使用，再见！\n")
            sys.exit(0)
        else:
            print("  无效选项，请重新输入")
            press_enter_to_continue()


# ---------- 入口 ----------

def main():
    """程序入口"""
    clear_screen()
    if not login():
        sys.exit(1)
    main_menu()


if __name__ == "__main__":
    main()
