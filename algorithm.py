import time

# Birim başına en fazla kaç “puan yükseldi” satırı yazılsın; fazlası özetlenir (süre + arayüz).
_MAX_DETAIL_IMPROVEMENT_LOGS_PER_UNIT = 8


def solve_bounded_knapsack(products, budget, log_callback=None, log_delay=0.0):
    budget = int(budget)

    expanded_items = []

    for product in products:
        for _ in range(product["quantity"]):
            expanded_items.append({
                "name": product["name"],
                "price": int(product["price"]),
                "importance": int(product["importance"])
            })

    dp = [0] * (budget + 1)
    selected = [[] for _ in range(budget + 1)]

    def log(message):
        if log_callback:
            log_callback(message)
            if log_delay > 0:
                time.sleep(log_delay)

    total_units = len(expanded_items)
    log(
        f"Hesaplama başladı: {total_units} birim ürün, bütçe {budget}. "
        f"Her birimde ilk birkaç DP iyileşmesi ayrıntılı; sonrası özet (süre için sınır)."
    )

    for item in expanded_items:
        price = item["price"]
        importance = item["importance"]
        name = item["name"]

        log(f"--- {name} inceleniyor (Fiyat: {price}, Önem: {importance}) ---")

        improvement_count = 0
        truncated_notice_shown = False

        for current_budget in range(budget, price - 1, -1):
            previous_value = dp[current_budget]
            new_value = dp[current_budget - price] + importance

            if new_value > previous_value:
                dp[current_budget] = new_value
                selected[current_budget] = selected[current_budget - price] + [item]
                improvement_count += 1
                if improvement_count <= _MAX_DETAIL_IMPROVEMENT_LOGS_PER_UNIT:
                    log(
                        f"Bütçe {current_budget} için: {name} eklendi, "
                        f"toplam puan {previous_value} -> {new_value} yükseldi."
                    )
                elif not truncated_notice_shown:
                    log(
                        "  … (aynı birimde çok sayıda benzer DP güncellemesi: "
                        f"ayrıntı kısaltıldı, toplam sayı birim sonunda)"
                    )
                    truncated_notice_shown = True

        if improvement_count > _MAX_DETAIL_IMPROVEMENT_LOGS_PER_UNIT:
            log(f"  → Bu birimde toplam {improvement_count} DP iyileştirmesi yapıldı.")
        elif improvement_count == 0:
            log("  (Bu birim bu aşamada hiçbir bütçe için iyileştirme getirmedi.)")

    best_items = selected[budget]

    grouped = {}

    for item in best_items:
        name = item["name"]

        if name not in grouped:
            grouped[name] = {
                "name": name,
                "price": item["price"],
                "quantity": 0,
                "importance": item["importance"]
            }

        grouped[name]["quantity"] += 1

    total_cost = sum(item["price"] * item["quantity"] for item in grouped.values())
    total_importance = sum(item["importance"] * item["quantity"] for item in grouped.values())

    log(f"Optimum çözüm bulundu, toplam önem puanı: {total_importance}")

    return {
        "selected_items": list(grouped.values()),
        "total_cost": total_cost,
        "remaining_budget": budget - total_cost,
        "total_importance": total_importance
    }