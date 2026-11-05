# Дополнительная выборка LegalBench-RU

Источник: https://github.com/AlsKozlov/legalbench-ru , проверенная версия `090163977d0e9a58a5887a38ec144f95cb37e464` (v0.3). Это сторонний набор коротких заданий, а не официальный источник права и не замена собственной рубрике проверки готового документа. В исходном корпусе задания помечены `needs_expert_review`; до юридической проверки эталона не включать их в приемочный балл.

## Выборка для практики пользователя

| Область | Путь к заданию | Идентификаторы экземпляров |
|---|---|---|
| Налоговая проверка | `tasks/rule-application-tax/test.jsonl` | `vozrazheniya-na-akt-srok`, `vichet-nds-realnost-sdelki`, `dosudebnoe-objalovanie-obyazatelno` |
| Налоговый вывод | `tasks/rule-conclusion-tax/test.jsonl` | `tax-vozrazheniya-akt-1-mesyac`, `tax-vychet-realnost-54-1`, `tax-isk-as-3-mesyaca` |
| Закупки и РНП | `tasks/rule-conclusion-procurement/test.jsonl` | `rnp-disqualification-2-years`, `rnp-period-expired`, `rnp-rehabilitation-discretionary`, `fas-decision-court-appeal`, `complaint-deadline-missed` |
| Поиск сведений о РНП | `tasks/tool-use-rnp/test.jsonl` | `negative-rnp-appeal-strategy` |
| Арбитражный процесс | `tasks/rule-application-litigation/test.jsonl` | `pretenzionnyy-poryadok-as-30-dney`, `apellyaciya-as-1-mesyac`, `kassaciya-as-2-mesyaca`, `snizhenie-neustoyki-333` |
| Судебная аргументация | `tasks/rhetorical-litigation/test.jsonl` | `rhet-grounds-reversal-rassmotrenie-otsutstvie-storony`, `rhet-rol-zloupotreblenie-pravom-argument` |

## Порядок применения

1. Закрепить указанную версию источника; проверить лицензию, условия задания и эталон по действующей на юридически значимую дату норме и первичному судебному источнику. Исправить или исключить ошибочный эталон с записью основания.
2. Дать исходный вопрос одной и той же модели до и после изменения навыка при одинаковых инструментах, дате права и доступе к источникам. Не передавать эталон исполнителю.
3. Оценить каждый ответ по праву и обоснованию независимо от автоматического совпадения с меткой. Отдельно измерить фактическую проверку источников, наличие выдуманных ссылок и применимость к конкретному делу.
4. Применить правила сопоставления из `benchmark-protocol.md`. Короткие ответы сравнивать только с короткими ответами; длинные процессуальные документы проверять собственной рубрикой и исходными материалами дела.

Техническая самопроверка исходного оценщика на четырех группах (`rule-application-tax`, `rule-conclusion-procurement`, `rule-application-litigation`, `rhetorical-litigation`) дала 39/39 в режиме `oracle` и 0/39 в режиме `stub`. Это подтверждает базовую работу оценщика на этих экземплярах, но ничего не говорит о качестве наших навыков или корректности эталонов.
