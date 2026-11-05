# Формат входных данных

## JSON

```json
{
  "claim_amount": 6500000,
  "litigation": {
    "success_probability": 0.65,
    "recovery_probability": 0.8,
    "months_to_cash": 18,
    "annual_discount_rate": 0.18,
    "legal_costs": 500000,
    "enforcement_costs_if_success": 100000,
    "adverse_costs_if_loss": 150000,
    "counterclaim_exposure": 0,
    "counterclaim_loss_probability": 0
  },
  "settlement": {
    "amount": 4000000,
    "payment_probability": 0.95,
    "months_to_cash": 3,
    "annual_discount_rate": 0.18,
    "transaction_costs": 50000
  },
  "sensitivity_step": 0.1
}
```

Все суммы задаются в одной валюте. Вероятности задаются числами от 0 до 1. Ставка дисконтирования задается годовой долей: `0.18` означает 18 процентов.

## Формулы

Приведенное ожидаемое взыскание:

`claim_amount * success_probability * recovery_probability / (1 + annual_discount_rate) ** (months_to_cash / 12)`

Ожидаемая приведенная стоимость суда:

`приведенное взыскание - legal_costs - success_probability * enforcement_costs_if_success - (1 - success_probability) * adverse_costs_if_loss - counterclaim_exposure * counterclaim_loss_probability`

Ожидаемая приведенная стоимость мирового соглашения:

`amount * payment_probability / (1 + annual_discount_rate) ** (months_to_cash / 12) - transaction_costs`

Пороговая сумма мирового соглашения равна сумме, при которой ожидаемая приведенная стоимость мирового соглашения совпадает с ожидаемой приведенной стоимостью суда. Отрицательный порог требует содержательной проверки исходных данных и неблагоприятного сценария.

Расходы в модели считаются немедленными и не дисконтируются. Если график расходов существенен, рассчитать его отдельно и заменить агрегированное значение приведенной стоимостью расходов.
