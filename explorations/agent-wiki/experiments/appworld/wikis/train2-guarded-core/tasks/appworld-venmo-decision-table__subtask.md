---
type: subtask
slug: appworld-venmo-decision-table
title: AppWorld Venmo Decision Table
parent_session_id: appworld_train2
parent_summary: summaries/index.md
tags: [appworld, venmo, phone, contacts, decision-table, payment-requests, social-feed]
verified_at: 2026-06-10
sources:
  - benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json
  - benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/6ea6792_3.json
---

# AppWorld Venmo Decision Table

Use this page as a cheap routing layer before reading a full skill.

## Decision Table

| Current task shape | Read skill? | Transfer from train | Do not transfer |
|---|---:|---|---|
| Like Venmo social-feed transactions filtered by contact relationship and time range | Yes: `like-venmo-transactions-involving-relatives` | Log in, get contacts, compute current task's time range, page social feed, match sender or receiver email, call `venmo.like_transaction` only for matching transaction IDs | Source dates, relationship values, people, emails, transaction IDs |
| Accept or approve pending received Venmo payment requests from contact relationship groups | Yes: `accept-venmo-payment-requests-from-contacts` | Log in, page `venmo.show_received_payment_requests(status="pending")`, get contacts, match request sender email, call `venmo.approve_payment_request` | Source request IDs, people, emails, passwords |
| Remind, deny, create, or otherwise handle Venmo payment requests | No direct skill | Reuse only contact filtering and pagination. Inspect API docs for the requested action endpoint. | Do not approve a request unless the task says accept/approve |
| Answer a question about Venmo transactions, payments, totals, counts, or social feed | No direct skill | Reuse only data gathering, pagination, relationship matching, and time-window filtering. Return the requested answer through `complete_task(answer=...)`. | Do not like, update, create, approve, deny, or remind records unless requested |
| Any non-Venmo app task | No | None from this wiki | Do not read Venmo skills |

## Core Pattern From Train

For relationship-based Venmo tasks, the train trajectories used the phone app as
the relationship source. Contacts were paged through `phone.search_contacts`,
then filtered by the `relationships` field. Venmo records were matched against
contact emails, not names.

For temporal Venmo tasks, the train trajectory obtained the current date from
the runtime or phone app, computed complete day boundaries, paged the Venmo data
source, and filtered records with runtime code before mutating anything.

For payment-request tasks, the train trajectory distinguished received pending
requests from other request states before taking action.

## Sources

- [social-feed transaction liking summary](../summaries/appworld__aw_react_train2_baseline__2a163ab_2.md)
- [payment-request approval summary](../summaries/appworld__aw_react_train2_baseline__6ea6792_3.md)
