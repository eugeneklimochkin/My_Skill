#!/usr/bin/env python3
import argparse
import json
from datetime import date
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path

getcontext().prec = 28
MONEY = Decimal("0.01")


def decimal_value(value, field):
    try:
        return Decimal(str(value))
    except Exception as exc:
        raise ValueError(f"Некорректное значение {field}: {value}") from exc


def count_days(item):
    start = date.fromisoformat(item["start"])
    end = date.fromisoformat(item["end"])
    if end < start:
        raise ValueError("Дата окончания раньше даты начала")
    days = (end - start).days
    if item.get("include_start", False):
        days += 1
    if not item.get("include_end", True):
        days -= 1
    if days < 0:
        raise ValueError("Получено отрицательное число дней")
    return days


def apply_cap(value, amount, item):
    limits = []
    if item.get("cap_percent") is not None:
        limits.append(amount * decimal_value(item["cap_percent"], "cap_percent") / Decimal("100"))
    if item.get("cap_amount") is not None:
        limits.append(decimal_value(item["cap_amount"], "cap_amount"))
    return min([value, *limits]) if limits else value


def calculate_line(item):
    amount = decimal_value(item["amount"], "amount")
    rate = decimal_value(item["rate_percent"], "rate_percent")
    days = count_days(item)
    line_type = item["type"]
    if line_type == "annual_interest":
        denominator = Decimal(str(item.get("days_in_year", 365)))
        raw = amount * rate / Decimal("100") * Decimal(days) / denominator
    elif line_type == "daily_penalty":
        raw = amount * rate / Decimal("100") * Decimal(days)
    else:
        raise ValueError(f"Неподдерживаемый тип: {line_type}")
    capped = apply_cap(raw, amount, item)
    return {
        "label": item.get("label", ""),
        "type": line_type,
        "amount": str(amount),
        "rate_percent": str(rate),
        "days": days,
        "raw_result": str(raw),
        "result": str(capped.quantize(MONEY, rounding=ROUND_HALF_UP)),
        "cap_applied": capped != raw,
    }


def main():
    parser = argparse.ArgumentParser(description="Проверяемый расчет процентов и неустойки")
    parser.add_argument("input", type=Path, help="Путь к JSON с массивом lines")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    rows = [calculate_line(item) for item in payload.get("lines", [])]
    total = sum((Decimal(row["result"]) for row in rows), Decimal("0"))
    print(json.dumps({"lines": rows, "total": str(total.quantize(MONEY))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
