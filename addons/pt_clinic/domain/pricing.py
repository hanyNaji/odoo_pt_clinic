from typing import Iterable, Optional


def apply_discount(base_amount: float, discount_type: str, discount_value: float) -> float:
    """Return discounted amount using fixed amount or percentage discount."""
    amount = max(base_amount, 0.0)
    value = max(discount_value, 0.0)
    if discount_type == "percent":
        return max(amount - (amount * value / 100.0), 0.0)
    if discount_type == "fixed":
        return max(amount - value, 0.0)
    return amount


def best_promo_price(base_amount: float, promo_prices: Iterable[float]) -> float:
    """Pick the best non-negative promotional price, fallback to base price."""
    valid = [p for p in promo_prices if p is not None and p >= 0.0]
    if not valid:
        return max(base_amount, 0.0)
    return min(valid)


def resolve_contract_price(
    default_service_price: float,
    contract_price: Optional[float],
    contract_discount_percent: Optional[float],
) -> float:
    """Resolve service price from contract fixed price or contract discount."""
    if contract_price is not None and contract_price >= 0.0:
        return contract_price
    if contract_discount_percent is not None and contract_discount_percent > 0:
        return apply_discount(default_service_price, "percent", contract_discount_percent)
    return max(default_service_price, 0.0)

