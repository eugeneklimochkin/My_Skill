#!/usr/bin/env python3
import json
import math
import sys
from pathlib import Path


def load_input():
    if len(sys.argv) > 2:
        raise SystemExit("usage: compare_scenarios.py [input.json]")
    if len(sys.argv) == 2:
        with Path(sys.argv[1]).open("r", encoding="utf-8") as source:
            return json.load(source)
    return json.load(sys.stdin)


def number(value, name, minimum=0.0):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    value = float(value)
    if not math.isfinite(value) or value < minimum:
        raise ValueError(f"{name} must be finite and at least {minimum}")
    return value


def probability(value, name):
    value = number(value, name)
    if value > 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return value


def discount_factor(rate, months):
    if rate <= -1:
        raise ValueError("annual_discount_rate must be greater than -1")
    return (1 + rate) ** (months / 12)


def litigation_value(claim_amount, params, success_probability=None):
    success = probability(
        params.get("success_probability", 0),
        "litigation.success_probability",
    ) if success_probability is None else success_probability
    recovery = probability(
        params.get("recovery_probability", 0),
        "litigation.recovery_probability",
    )
    months = number(params.get("months_to_cash", 0), "litigation.months_to_cash")
    rate = number(
        params.get("annual_discount_rate", 0),
        "litigation.annual_discount_rate",
        minimum=0,
    )
    legal_costs = number(params.get("legal_costs", 0), "litigation.legal_costs")
    enforcement_costs = number(
        params.get("enforcement_costs_if_success", 0),
        "litigation.enforcement_costs_if_success",
    )
    adverse_costs = number(
        params.get("adverse_costs_if_loss", 0),
        "litigation.adverse_costs_if_loss",
    )
    counterclaim = number(
        params.get("counterclaim_exposure", 0),
        "litigation.counterclaim_exposure",
    )
    counterclaim_probability = probability(
        params.get("counterclaim_loss_probability", 0),
        "litigation.counterclaim_loss_probability",
    )

    expected_recovery_nominal = claim_amount * success * recovery
    expected_recovery_pv = expected_recovery_nominal / discount_factor(rate, months)
    expected_enforcement_costs = success * enforcement_costs
    expected_adverse_costs = (1 - success) * adverse_costs
    expected_counterclaim = counterclaim * counterclaim_probability
    expected_net_pv = (
        expected_recovery_pv
        - legal_costs
        - expected_enforcement_costs
        - expected_adverse_costs
        - expected_counterclaim
    )
    return {
        "success_probability": success,
        "expected_recovery_nominal": expected_recovery_nominal,
        "expected_recovery_pv": expected_recovery_pv,
        "expected_enforcement_costs": expected_enforcement_costs,
        "expected_adverse_costs": expected_adverse_costs,
        "expected_counterclaim": expected_counterclaim,
        "expected_net_pv": expected_net_pv,
    }


def settlement_value(params):
    amount = number(params.get("amount", 0), "settlement.amount")
    payment_probability = probability(
        params.get("payment_probability", 0),
        "settlement.payment_probability",
    )
    months = number(params.get("months_to_cash", 0), "settlement.months_to_cash")
    rate = number(
        params.get("annual_discount_rate", 0),
        "settlement.annual_discount_rate",
        minimum=0,
    )
    transaction_costs = number(
        params.get("transaction_costs", 0),
        "settlement.transaction_costs",
    )
    expected_payment_nominal = amount * payment_probability
    expected_payment_pv = expected_payment_nominal / discount_factor(rate, months)
    return {
        "amount": amount,
        "payment_probability": payment_probability,
        "expected_payment_nominal": expected_payment_nominal,
        "expected_payment_pv": expected_payment_pv,
        "transaction_costs": transaction_costs,
        "expected_net_pv": expected_payment_pv - transaction_costs,
        "months_to_cash": months,
        "annual_discount_rate": rate,
    }


def rounded(value):
    return round(value + 0.0, 2)


def main():
    data = load_input()
    claim_amount = number(data.get("claim_amount", 0), "claim_amount")
    litigation_params = data.get("litigation")
    settlement_params = data.get("settlement")
    if not isinstance(litigation_params, dict) or not isinstance(settlement_params, dict):
        raise ValueError("litigation and settlement must be objects")

    litigation = litigation_value(claim_amount, litigation_params)
    settlement = settlement_value(settlement_params)
    payment_probability = settlement["payment_probability"]
    if payment_probability == 0:
        break_even = None
    else:
        required_payment_pv = litigation["expected_net_pv"] + settlement["transaction_costs"]
        break_even = (
            required_payment_pv
            * discount_factor(
                settlement["annual_discount_rate"],
                settlement["months_to_cash"],
            )
            / payment_probability
        )

    step = probability(data.get("sensitivity_step", 0.1), "sensitivity_step")
    base_success = litigation["success_probability"]
    sensitivity = []
    for label, success in (
        ("lower", max(0.0, base_success - step)),
        ("base", base_success),
        ("upper", min(1.0, base_success + step)),
    ):
        scenario = litigation_value(claim_amount, litigation_params, success)
        sensitivity.append(
            {
                "scenario": label,
                "success_probability": success,
                "litigation_expected_net_pv": rounded(scenario["expected_net_pv"]),
            }
        )

    output = {
        "claim_amount": rounded(claim_amount),
        "litigation": {key: rounded(value) for key, value in litigation.items()},
        "settlement": {
            key: rounded(value)
            for key, value in settlement.items()
            if key not in {"months_to_cash", "annual_discount_rate"}
        },
        "settlement_minus_litigation_pv": rounded(
            settlement["expected_net_pv"] - litigation["expected_net_pv"]
        ),
        "break_even_settlement_amount": None if break_even is None else rounded(break_even),
        "sensitivity": sensitivity,
    }
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit(f"input error: {exc}") from exc
