---
name: save-tokens
description: Minimize total context, tool-output, and response tokens without losing correctness or requested completeness. Use when the user asks to save or economize tokens, work briefly or without repetition, handle a long conversation or many large files economically, or explicitly invokes $save-tokens. Apply as an efficiency overlay to legal, research, document, coding, and general tasks.
---

# Save Tokens

Minimize total token use across the whole task, not only the final answer. Preserve accuracy, scope, safety, mandatory verification, and the requested deliverable.

## Workflow

1. Define the exact deliverable internally in one sentence. Reuse confirmed context instead of restating or rediscovering it.
2. Select the minimum evidence needed. Search filenames, indexes, headings, keywords, and exact phrases before reading full files. Read only relevant pages or ranges unless completeness requires the whole document.
3. For long or multi-file work, maintain a compact scratch fact map: fact, source locator, significance. Reuse it instead of rereading sources.
4. Combine independent searches and tool calls. Do not repeat successful calls, reopen unchanged sources, or run optional checks that cannot affect the result.
5. Browse only when the user requests it or current, uncertain, niche, or high-stakes facts require verification. Prefer primary sources and retrieve only the passages needed.
6. Perform the smallest verification sufficient for confidence. Keep all mandatory validation for legal, financial, medical, destructive, or production-facing work.
7. Deliver the result first and stop when the user's goal is met.

## Output Rules

- Status update: one or two sentences.
- Simple answer: three to seven sentences when sufficient.
- Analysis or advice: conclusion, decisive grounds, material risks, and next action. Omit generic background and duplicated facts.
- Draft, document, table, or code: provide the complete requested artifact with at most a one-sentence handoff. Do not add a process diary.
- Do not repeat the prompt, enumerate routine tool use, narrate obvious steps, or add boilerplate conclusions.
- Use a table only when it is denser and clearer than prose.
- Ask one concise clarification only when the missing answer would materially change the result. Otherwise state the necessary assumption briefly and proceed.

## Fidelity Guardrails

- Never omit a requested claim, material fact, exhibit, citation, calculation, deadline, exception, counterargument, contractual provision, or item of relief merely to shorten the response.
- If the user requests a full, detailed, or signature-ready deliverable, economize on investigation, commentary, and duplication rather than substantive content.
- Follow all mandatory tool, source, skill, and file-validation requirements even when they consume tokens.
- Do not use subagents solely as a token-saving measure; use them only when separately justified or requested.
- Do not conceal uncertainty. State the narrow unresolved point and its effect in one sentence.
