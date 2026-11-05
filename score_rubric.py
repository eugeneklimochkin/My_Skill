#!/usr/bin/env python3
"""Aggregate criterion decisions for Harvey LAB RF.

The script does not make legal decisions. It validates and aggregates decisions
already made by a lawyer or evaluator.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PRIORITY_ALIASES = {
    "b": "blocking",
    "blocking": "blocking",
    "блокирующий": "blocking",
    "r": "required",
    "required": "required",
    "обязательный": "required",
    "a": "additional",
    "additional": "additional",
    "дополнительный": "additional",
}

VERDICT_ALIASES = {
    "pass": "pass",
    "пройден": "pass",
    "пройдено": "pass",
    "fail": "fail",
    "не пройден": "fail",
    "не пройдено": "fail",
    "na": "na",
    "n/a": "na",
    "неприменимо": "na",
    "unverified": "unverified",
    "не проверено": "unverified",
    "не подтверждено": "unverified",
}

GATE_PRIORITIES = {"blocking", "required"}
NON_PASSING = {"fail", "unverified"}


class RubricError(ValueError):
    """Raised when an assessment does not match the required schema."""


def _normalize(value: Any, aliases: dict[str, str], field: str, criterion_id: str) -> str:
    if not isinstance(value, str):
        raise RubricError(f"{criterion_id}: поле {field} должно быть строкой")
    key = value.strip().lower()
    if key not in aliases:
        allowed = ", ".join(sorted(set(aliases.values())))
        raise RubricError(f"{criterion_id}: недопустимое значение {field}; допустимо: {allowed}")
    return aliases[key]


def normalize_criteria(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("criteria")
    if not isinstance(raw, list) or not raw:
        raise RubricError("Поле criteria должно быть непустым массивом")

    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise RubricError(f"Критерий #{index} должен быть объектом")

        criterion_id = str(item.get("id", "")).strip()
        if not criterion_id:
            raise RubricError(f"Критерий #{index}: отсутствует id")
        if criterion_id in seen_ids:
            raise RubricError(f"Повторяющийся id критерия: {criterion_id}")
        seen_ids.add(criterion_id)

        priority = _normalize(item.get("priority"), PRIORITY_ALIASES, "priority", criterion_id)
        verdict = _normalize(item.get("verdict"), VERDICT_ALIASES, "verdict", criterion_id)
        reason = str(item.get("reason", "")).strip()
        if verdict in {"fail", "na", "unverified"} and not reason:
            raise RubricError(f"{criterion_id}: для {verdict} требуется reason")

        normalized.append(
            {
                "id": criterion_id,
                "title": str(item.get("title", "")).strip(),
                "priority": priority,
                "verdict": verdict,
                "reason": reason,
                "source": str(item.get("source", "")).strip(),
            }
        )

    return normalized


def _finding(item: dict[str, Any]) -> dict[str, str]:
    return {
        "id": item["id"],
        "title": item["title"],
        "verdict": item["verdict"],
        "reason": item["reason"],
        "source": item["source"],
    }


def score(payload: dict[str, Any]) -> dict[str, Any]:
    criteria = normalize_criteria(payload)
    applicable = [item for item in criteria if item["verdict"] != "na"]
    gate = [item for item in applicable if item["priority"] in GATE_PRIORITIES]
    if not gate:
        raise RubricError("Нет применимых blocking или required критериев")

    failed_blocking = [
        item for item in gate if item["priority"] == "blocking" and item["verdict"] in NON_PASSING
    ]
    failed_required = [
        item for item in gate if item["priority"] == "required" and item["verdict"] in NON_PASSING
    ]
    additional_findings = [
        item
        for item in applicable
        if item["priority"] == "additional" and item["verdict"] in NON_PASSING
    ]

    if failed_blocking:
        status = "НЕПРИГОДНО"
    elif failed_required:
        status = "ТРЕБУЕТ ДОРАБОТКИ"
    else:
        status = "ГОТОВО"

    all_pass = status == "ГОТОВО"
    n_passed = sum(item["verdict"] == "pass" for item in applicable)
    n_gate_passed = sum(item["verdict"] == "pass" for item in gate)
    counts = Counter(item["verdict"] for item in criteria)

    return {
        "task_id": str(payload.get("task_id", "")).strip(),
        "status": status,
        "all_pass": all_pass,
        "score": 1.0 if all_pass else 0.0,
        "criterion_pass_rate": round(n_passed / len(applicable), 4) if applicable else 0.0,
        "gate_pass_rate": round(n_gate_passed / len(gate), 4),
        "n_criteria": len(criteria),
        "n_applicable": len(applicable),
        "n_passed": n_passed,
        "n_gate": len(gate),
        "n_gate_passed": n_gate_passed,
        "counts": {
            "pass": counts["pass"],
            "fail": counts["fail"],
            "na": counts["na"],
            "unverified": counts["unverified"],
        },
        "failed_blocking": [_finding(item) for item in failed_blocking],
        "failed_required": [_finding(item) for item in failed_required],
        "additional_findings": [_finding(item) for item in additional_findings],
    }


def load_payload(path: str) -> dict[str, Any]:
    if path == "-":
        data = json.load(sys.stdin)
    else:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RubricError("Верхний уровень JSON должен быть объектом")
    return data


def self_test() -> None:
    base = {
        "task_id": "self-test",
        "criteria": [
            {
                "id": "B-1",
                "title": "Блокирующий",
                "priority": "blocking",
                "verdict": "pass",
            },
            {
                "id": "R-1",
                "title": "Обязательный",
                "priority": "required",
                "verdict": "pass",
            },
            {
                "id": "A-1",
                "title": "Дополнительный",
                "priority": "additional",
                "verdict": "na",
                "reason": "Не относится к заданию",
            },
        ],
    }
    ready = score(base)
    assert ready["status"] == "ГОТОВО"
    assert ready["all_pass"] is True
    assert ready["score"] == 1.0

    required_fail = json.loads(json.dumps(base, ensure_ascii=False))
    required_fail["criteria"][1]["verdict"] = "fail"
    required_fail["criteria"][1]["reason"] = "Требование отсутствует"
    revise = score(required_fail)
    assert revise["status"] == "ТРЕБУЕТ ДОРАБОТКИ"
    assert revise["all_pass"] is False

    blocking_fail = json.loads(json.dumps(base, ensure_ascii=False))
    blocking_fail["criteria"][0]["verdict"] = "unverified"
    blocking_fail["criteria"][0]["reason"] = "Источник недоступен"
    unsuitable = score(blocking_fail)
    assert unsuitable["status"] == "НЕПРИГОДНО"
    assert unsuitable["score"] == 0.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Подсчитать итог Harvey LAB RF по готовым оценкам критериев"
    )
    parser.add_argument("assessment", nargs="?", help="Путь к JSON или - для stdin")
    parser.add_argument("-o", "--output", help="Записать итоговый JSON в файл")
    parser.add_argument("--compact", action="store_true", help="Вывести JSON без отступов")
    parser.add_argument("--self-test", action="store_true", help="Запустить встроенные тесты")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        print("self-test: ok")
        return 0

    if not args.assessment:
        print("Ошибка: укажите assessment или --self-test", file=sys.stderr)
        return 2

    try:
        result = score(load_payload(args.assessment))
    except (OSError, json.JSONDecodeError, RubricError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 2

    indent = None if args.compact else 2
    rendered = json.dumps(result, ensure_ascii=False, indent=indent) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
