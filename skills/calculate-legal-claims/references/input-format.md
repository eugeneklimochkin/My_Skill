# Формат входного JSON

Передать объект с массивом lines. Поддерживаются типы annual_interest и daily_penalty.

Пример:

    {
      "lines": [
        {
          "label": "Проценты за первый период",
          "type": "annual_interest",
          "amount": "100000.00",
          "rate_percent": "10",
          "start": "2026-01-01",
          "end": "2026-01-11",
          "include_start": false,
          "include_end": true,
          "days_in_year": 365
        },
        {
          "label": "Договорная неустойка",
          "type": "daily_penalty",
          "amount": "50000.00",
          "rate_percent": "0.1",
          "start": "2026-02-01",
          "end": "2026-02-10",
          "include_start": false,
          "include_end": true,
          "cap_percent": "10"
        }
      ]
    }

rate_percent указывать в процентах: 10 означает 10 процентов годовых, 0.1 означает 0,1 процента в день.

Если ставка менялась, создавать отдельную строку для каждого периода. Если долг уменьшался, разбивать период на дату каждого платежа.
