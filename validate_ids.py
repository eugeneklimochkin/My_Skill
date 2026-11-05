#!/usr/bin/env python3
"""Normalize and validate Russian INN, OGRN and OGRNIP identifiers."""

from __future__ import annotations

import argparse
import json
import re
import sys


def normalize(value: str) -> str:
    return re.sub(r"[\s\-]", "", value.strip())


def weighted_digit(number: str, coefficients: list[int]) -> int:
    return sum(int(digit) * coefficient for digit, coefficient in zip(number, coefficients)) % 11 % 10


def validate_inn10(number: str) -> bool:
    coefficients = [2, 4, 10, 3, 5, 9, 4, 6, 8]
    return weighted_digit(number[:9], coefficients) == int(number[9])


def validate_inn12(number: str) -> bool:
    coefficients_11 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    coefficients_12 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    return (
        weighted_digit(number[:10], coefficients_11) == int(number[10])
        and weighted_digit(number[:11], coefficients_12) == int(number[11])
    )


def validate_ogrn(number: str) -> bool:
    return int(number[:12]) % 11 % 10 == int(number[12])


def validate_ogrnip(number: str) -> bool:
    return int(number[:14]) % 13 % 10 == int(number[14])


def inspect_identifier(raw: str) -> dict[str, object]:
    number = normalize(raw)
    result: dict[str, object] = {
        "input": raw,
        "normalized": number,
        "type": "unknown",
        "valid": False,
    }

    if not number.isdigit():
        result["reason"] = "Identifier contains characters other than digits, spaces or hyphens."
        return result

    validators = {
        10: ("INN legal entity", validate_inn10),
        12: ("INN individual or sole proprietor", validate_inn12),
        13: ("OGRN", validate_ogrn),
        15: ("OGRNIP", validate_ogrnip),
    }
    selected = validators.get(len(number))
    if selected is None:
        result["reason"] = "Expected 10 or 12 digits for INN, 13 for OGRN, or 15 for OGRNIP."
        return result

    identifier_type, validator = selected
    result["type"] = identifier_type
    result["valid"] = validator(number)
    if not result["valid"]:
        result["reason"] = "Check digit does not match."
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("identifiers", nargs="*", help="INN, OGRN or OGRNIP values")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    identifiers = args.identifiers
    if not identifiers and not sys.stdin.isatty():
        identifiers = [line.strip() for line in sys.stdin if line.strip()]
    if not identifiers:
        print("Provide at least one identifier.", file=sys.stderr)
        return 2

    results = [inspect_identifier(value) for value in identifiers]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(item["valid"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
