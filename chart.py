"""
图表绘制模块 - 使用 matplotlib 生成饼图、柱状图和趋势折线图
"""

import platform

# 必须在 import pyplot 之前设置后端
import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from finance import get_records, filter_by_month


# ---------- 中文字体自动配置 ----------

def _setup_chinese_font():
    """
    根据操作系统自动检测并设置中文字体，
    避免图表中出现中文乱码或方框
    """
    system = platform.system()

    if system == "Windows":
        candidates = ["Microsoft YaHei", "SimHei", "KaiTi", "SimSun", "FangSong"]
    elif system == "Darwin":
        candidates = [
            "PingFang SC", "Heiti SC", "STHeiti",
            "Apple LiGothic", "Arial Unicode MS"
        ]
    else:  # Linux
        candidates = [
            "WenQuanYi Micro Hei", "WenQuanYi Zen Hei",
            "Noto Sans CJK SC", "Noto Sans SC",
            "Droid Sans Fallback", "DejaVu Sans"
        ]

    for font_name in candidates:
        try:
            fm.findfont(font_name, fallback_to_default=False)
            plt.rcParams["font.sans-serif"] = [font_name, "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
            return
        except Exception:
            continue

    # 兜底：遍历系统所有字体寻找中文支持
    for f in fm.fontManager.ttflist:
        try:
            plt.rcParams["font.sans-serif"] = [f.name, "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
            return
        except Exception:
            continue

    # 最终兜底
    plt.rcParams["axes.unicode_minus"] = False


_setup_chinese_font()

# ---------- 颜色主题 ----------
COLORS_PIE = plt.cm.Set3
INCOME_COLOR = "#4CAF50"
EXPENSE_COLOR = "#F44336"
BALANCE_COLOR = "#2196F3"


# ---------- 图表生成 ----------

def generate_pie_chart(record_type="expense", year_month=None):
    """
    生成收支分类占比饼图
    参数:
        record_type: 'income' 或 'expense'
        year_month:  可选，如 '2026-04'，限定月份
    """
    records = get_records()
    if year_month:
        records = filter_by_month(records, year_month)

    # 按分类汇总
    stats = {}
    for r in records:
        if r["type"] == record_type:
            stats[r["category"]] = stats.get(r["category"], 0) + r["amount"]

    if not stats:
        print("  没有可用于生成饼图的数据，请先添加记录")
        return

    type_cn = "收入" if record_type == "income" else "支出"
    title_suffix = f"（{year_month}）" if year_month else "（全部）"

    labels = list(stats.keys())
    sizes = list(stats.values())
    colors = COLORS_PIE(range(len(labels)))

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        pctdistance=0.75,
        labeldistance=1.1
    )

    for t in texts:
        t.set_fontsize(10)
    for t in autotexts:
        t.set_fontsize(9)

    ax.set_title(f"{type_cn}分类占比{title_suffix}", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()


def generate_bar_chart(year_month=None):
    """
    生成收支分类对比柱状图（分组柱状图）
    参数:
        year_month: 可选，限定月份
    """
    records = get_records()
    if year_month:
        records = filter_by_month(records, year_month)

    # 分别汇总
    income_stats = {}
    expense_stats = {}
    for r in records:
        if r["type"] == "income":
            income_stats[r["category"]] = income_stats.get(r["category"], 0) + r["amount"]
        else:
            expense_stats[r["category"]] = expense_stats.get(r["category"], 0) + r["amount"]

    if not income_stats and not expense_stats:
        print("  没有可用于生成柱状图的数据，请先添加记录")
        return

    all_cats = sorted(set(list(income_stats.keys()) + list(expense_stats.keys())))
    income_vals = [income_stats.get(c, 0) for c in all_cats]
    expense_vals = [expense_stats.get(c, 0) for c in all_cats]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(all_cats))
    width = 0.35

    bars_in = ax.bar(
        [i - width / 2 for i in x], income_vals, width,
        label="收入", color=INCOME_COLOR, alpha=0.85
    )
    bars_ex = ax.bar(
        [i + width / 2 for i in x], expense_vals, width,
        label="支出", color=EXPENSE_COLOR, alpha=0.85
    )

    # 柱顶标注数值
    max_val = max(max(income_vals) if income_vals else 0,
                  max(expense_vals) if expense_vals else 0)
    for bar in bars_in:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2., h + max_val * 0.01,
                    f"¥{h:.0f}", ha="center", va="bottom", fontsize=8)
    for bar in bars_ex:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2., h + max_val * 0.01,
                    f"¥{h:.0f}", ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("分类", fontsize=12)
    ax.set_ylabel("金额（元）", fontsize=12)
    title_suffix = f"（{year_month}）" if year_month else "（全部）"
    ax.set_title(f"收支分类对比{title_suffix}", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(all_cats, rotation=30, ha="right", fontsize=9)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.show()


def generate_monthly_trend():
    """生成月度收支趋势折线图"""
    records = get_records()
    if not records:
        print("  没有可用于生成趋势图的数据，请先添加记录")
        return

    # 按月汇总
    monthly = {}
    for r in records:
        month = r["date"][:7]
        if month not in monthly:
            monthly[month] = {"income": 0, "expense": 0}
        monthly[month][r["type"]] += r["amount"]

    months = sorted(monthly.keys())
    income_data = [monthly[m]["income"] for m in months]
    expense_data = [monthly[m]["expense"] for m in months]
    balance_data = [monthly[m]["income"] - monthly[m]["expense"] for m in months]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(months, income_data, marker="o", linewidth=2, color=INCOME_COLOR, label="收入")
    ax.plot(months, expense_data, marker="s", linewidth=2, color=EXPENSE_COLOR, label="支出")
    ax.plot(months, balance_data, marker="^", linewidth=2, color=BALANCE_COLOR, label="结余")

    # 标注数据点
    for i, (inc, exp, bal) in enumerate(zip(income_data, expense_data, balance_data)):
        ax.annotate(
            f"¥{inc:.0f}", (months[i], inc),
            textcoords="offset points", xytext=(0, 10),
            ha="center", fontsize=8, color=INCOME_COLOR
        )
        ax.annotate(
            f"¥{exp:.0f}", (months[i], exp),
            textcoords="offset points", xytext=(0, -15),
            ha="center", fontsize=8, color=EXPENSE_COLOR
        )
        ax.annotate(
            f"¥{bal:.0f}", (months[i], bal),
            textcoords="offset points", xytext=(0, 10),
            ha="center", fontsize=8, color=BALANCE_COLOR
        )

    ax.set_xlabel("月份", fontsize=12)
    ax.set_ylabel("金额（元）", fontsize=12)
    ax.set_title("月度收支趋势", fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.show()
