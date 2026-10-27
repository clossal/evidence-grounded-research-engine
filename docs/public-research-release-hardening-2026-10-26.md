# Public Research Engine Release Hardening — 2026-10-26

## Security upgrade

The isolated public candidate was upgraded from Next.js `15.5.28` to `16.4.3`.
Node 20.20.2 meets Next 16.4.3's Node `>=20.9.0` requirement. React `18.3.1`
remains supported, with a Next 17 deprecation warning.

| Item | Before | After |
| --- | --- | --- |
| `next` | 15.5.28 | 16.4.3 |
| Nested Next `postcss` | 8.4.31 | 8.5.23 |
| `npm audit` | 1 high, 1 moderate | 0 findings |

Resolved inherited advisory IDs: `GHSA-6g55-p6wh-862q`,
`GHSA-r28c-9q8g-f849`, `GHSA-qx2v-qp2m-jg93`, and
`GHSA-fxqj-rqcc-2cmp`, formerly via `next@15.5.28 -> postcss@8.4.31`.
They require attacker-controlled CSS/source-map input during PostCSS processing.

The public backend safeguards (4/4), TypeScript, production build, browser
cited-answer interaction, citation navigation and allow-list audit passed.
Next's standard TypeScript migration is included. No private application files
were upgraded.

## Eight-case rerun

Final outcome: **3 source-supported answers, 2 correct negative/live
abstentions, and 3 safe answerable-question abstentions**. WDR strategies and
PHE policy/practice had relevant evidence but Qwen sometimes abstained;
Strategic Competition methodology pages fell outside the six-chunk context
budget. The validator now rejects natural-language insufficiency claims with
appended markers rather than misreporting them as cited answers.

## Decisions

| Release mode | Decision |
| --- | --- |
| Local demonstration | PASS, qualified: use verified successful questions and safe abstentions. |
| Source-only GitHub release | PASS: isolated fresh history, no remote, no private assets, clean audit. |
| Public hosting / comprehensive accuracy claim | BLOCKED: single-user/local design and answer-coverage limitations. |

