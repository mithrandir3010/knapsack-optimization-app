import time


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

    for item in expanded_items:
        price = item["price"]
        importance = item["importance"]
        name = item["name"]

        log(f"--- {name} inceleniyor (Fiyat: {price}, Önem: {importance}) ---")

        for current_budget in range(budget, price - 1, -1):
            previous_value = dp[current_budget]
            new_value = dp[current_budget - price] + importance

            if new_value > previous_value:
                dp[current_budget] = new_value
                selected[current_budget] = selected[current_budget - price] + [item]
                log(
                    f"Bütçe {current_budget} için: {name} eklendi, "
                    f"toplam puan {previous_value} -> {new_value} yükseldi."
                )
            else:
                log(f"Bütçe yetersiz veya verimsiz: {name} bu adımda değerlendirilmedi.")

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