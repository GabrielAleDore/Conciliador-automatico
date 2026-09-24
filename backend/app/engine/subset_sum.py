from decimal import Decimal
from typing import List, Optional, Callable, TypeVar

T = TypeVar('T')

def find_exact_subset_sum(
    candidates: List[T],
    target: Decimal,
    value_getter: Callable[[T], Decimal],
    max_k: int = 15
) -> Optional[List[T]]:
    """
    Encontra um subconjunto de itens cuja soma dos valores seja EXATAMENTE igual ao target.
    Usa branch & bound com poda determinística sobre centavos inteiros.
    Totalmente livre de erros de aproximação de ponto flutuante.
    """
    target_cents = int((target * 100).to_integral_value())
    
    valid_items = []
    for item in candidates:
        val = value_getter(item)
        val_cents = int((val * 100).to_integral_value())
        if 0 < val_cents <= target_cents:
            valid_items.append((val_cents, item))

    valid_items.sort(key=lambda x: x[0], reverse=True)

    n = len(valid_items)
    if n == 0:
        return None

    suffix_sums = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix_sums[i] = suffix_sums[i + 1] + valid_items[i][0]

    result: Optional[List[T]] = None

    def backtrack(idx: int, current_sum: int, chosen: List[T]):
        nonlocal result
        if result is not None:
            return

        if current_sum == target_cents and len(chosen) >= 2:
            result = list(chosen)
            return

        if idx >= n or len(chosen) >= max_k:
            return

        # Poda: soma de tudo restante não atinge a meta
        if current_sum + suffix_sums[idx] < target_cents:
            return

        for i in range(idx, n):
            val_cents, item = valid_items[i]
            if current_sum + val_cents > target_cents:
                continue

            chosen.append(item)
            backtrack(i + 1, current_sum + val_cents, chosen)
            chosen.pop()

            if result is not None:
                return

    backtrack(0, 0, [])
    return result
