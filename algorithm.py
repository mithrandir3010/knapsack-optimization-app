import time

# Bir meta-öğe (DP adımı) başına en fazla kaç “puan yükseldi” satırı; fazlası özetlenir.
_MAX_DETAIL_IMPROVEMENT_LOGS_PER_UNIT = 8


def _build_meta_items(products):
    """Sınırlı adet → 0/1 knapsack için O(log q) sanal paket (ikili ayrıştırma)."""
    meta = []
    for product in products:
        qty = int(product["quantity"])
        if qty <= 0:
            continue
        unit_p = int(product["price"])
        unit_imp = int(product["importance"])
        name = product["name"]

        power = 1
        remaining = qty
        while power <= remaining:
            bundle = power
            meta.append({
                "name": name,
                "unit_price": unit_p,
                "unit_importance": unit_imp,
                "bundle_qty": bundle,
                "bundle_price": unit_p * bundle,
                "bundle_importance": unit_imp * bundle,
            })
            remaining -= bundle
            power <<= 1
        if remaining > 0:
            bundle = remaining
            meta.append({
                "name": name,
                "unit_price": unit_p,
                "unit_importance": unit_imp,
                "bundle_qty": bundle,
                "bundle_price": unit_p * bundle,
                "bundle_importance": unit_imp * bundle,
            })
    return meta


def _aggregate_from_meta(picked):
    buckets = {}
    for m in picked:
        key = m["name"]
        if key not in buckets:
            buckets[key] = {
                "name": m["name"],
                "price": m["unit_price"],
                "importance": m["unit_importance"],
                "quantity": 0,
            }
        buckets[key]["quantity"] += m["bundle_qty"]
    return list(buckets.values())


def _reconstruct_from_layers(meta_items, budget, layers):
    """layers[mi] = mi. öğe işlenmeden önceki dp; layers[len(meta)] = son dp."""
    B = budget
    w = B
    picked = []
    for mi in range(len(meta_items) - 1, -1, -1):
        pre = layers[mi]
        post = layers[mi + 1]
        item = meta_items[mi]
        p = item["bundle_price"]
        v = item["bundle_importance"]
        if w < p:
            continue
        if post[w] == pre[w]:
            continue
        if post[w] == pre[w - p] + v:
            picked.append(item)
            w -= p
    return picked


def solve_bounded_knapsack(products, budget, log_callback=None, log_delay=0.0):
    budget = int(budget)

    def log(message):
        if log_callback:
            log_callback(message)
            if log_delay > 0:
                time.sleep(log_delay)

    meta_items = _build_meta_items(products)
    total_physical = sum(int(p["quantity"]) for p in products if int(p.get("quantity", 0)) > 0)
    B = budget

    layers = [[0] * (B + 1)]
    dp = layers[0][:]

    log(
        f"Hesaplama başladı: {len(meta_items)} sanal paket "
        f"(≈log₂ adet), toplam {total_physical} birim, bütçe {B}. "
        f"DP katmanları + güvenli geri izleme."
    )

    for mi, item in enumerate(meta_items):
        price = item["bundle_price"]
        importance = item["bundle_importance"]
        name = item["name"]
        bq = item["bundle_qty"]
        label = f"{name} [×{bq}]" if bq != 1 else name

        log(f"--- {label} inceleniyor (Paket fiyat: {price}, Paket önem: {importance}) ---")

        improvement_count = 0
        truncated_notice_shown = False

        for w in range(B, price - 1, -1):
            previous_value = dp[w]
            new_value = dp[w - price] + importance
            if new_value > previous_value:
                dp[w] = new_value
                improvement_count += 1
                if improvement_count <= _MAX_DETAIL_IMPROVEMENT_LOGS_PER_UNIT:
                    log(
                        f"Bütçe {w} için: {label} eklendi, "
                        f"toplam puan {previous_value} -> {new_value} yükseldi."
                    )
                elif not truncated_notice_shown:
                    log(
                        "  … (aynı pakette çok sayıda benzer DP güncellemesi: "
                        "ayrıntı kısaltıldı, toplam sayı paket sonunda)"
                    )
                    truncated_notice_shown = True

        if improvement_count > _MAX_DETAIL_IMPROVEMENT_LOGS_PER_UNIT:
            log(f"  → Bu pakette toplam {improvement_count} DP iyileştirmesi yapıldı.")
        elif improvement_count == 0:
            log("  (Bu paket bu aşamada hiçbir bütçe için iyileştirme getirmedi.)")

        layers.append(dp[:])

    picked = _reconstruct_from_layers(meta_items, B, layers)
    grouped_list = _aggregate_from_meta(picked)

    total_cost = sum(x["price"] * x["quantity"] for x in grouped_list)
    total_importance = sum(x["importance"] * x["quantity"] for x in grouped_list)

    log(f"Optimum çözüm bulundu, toplam önem puanı: {total_importance}")

    return {
        "selected_items": grouped_list,
        "total_cost": total_cost,
        "remaining_budget": budget - total_cost,
        "total_importance": total_importance,
    }
