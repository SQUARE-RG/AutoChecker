import json
import matplotlib.pyplot as plt

def main():
    with open("/root/code_check/clang_tidy_collect/collect_clang_tidy_checker/all_checker.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    category_data = data.get("data", {})
    categories = []
    counts = []
    for cat, checkers in category_data.items():
        categories.append(cat)
        counts.append(len(checkers))
    plt.figure(figsize=(14, 6))
    bars = plt.bar(categories, counts)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel("Checker Count")
    plt.title("Clang-Tidy Checker Count by Category")
    plt.tight_layout()
    # 在每个柱子上标注数量
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(count),
                 ha='center', va='bottom', fontsize=10)
    plt.savefig("/root/code_check/clang_tidy_collect/collect_clang_tidy_checker/checker_count_bar.png")
    plt.show()

    # 绘制饼图
    plt.figure(figsize=(8, 8))
    total = sum(counts)
    def make_label(cat, count):
        percent = count / total * 100
        return f"{cat}\n{percent:.1f}%"
    labels = [make_label(cat, count) for cat, count in zip(categories, counts)]
    plt.pie(counts, labels=labels, autopct=lambda pct: f"{pct:.1f}%", startangle=140)
    plt.title("Clang-Tidy Checker Category Proportion")
    plt.savefig("/root/code_check/clang_tidy_collect/collect_clang_tidy_checker/checker_count_pie.png")
    plt.show()

if __name__ == "__main__":
    main()
