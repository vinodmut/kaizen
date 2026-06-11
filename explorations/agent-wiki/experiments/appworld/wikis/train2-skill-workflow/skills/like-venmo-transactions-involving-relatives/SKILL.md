---
id: skill:like-venmo-transactions-involving-relatives
type: skill
name: like-venmo-transactions-involving-relatives
description: Like all Venmo transactions from a specified date involving any of the user's relatives, using only app APIs and contacts.
trigger: When you need to like all Venmo transactions from a given date involving any of the user's relatives (e.g., siblings) as found in the phone's contacts, and must use only app APIs.
agent: appworld-react-code
sources:
  - benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json
related_summary: summaries/appworld__aw_react_train2_baseline__2a163ab_2.md
verified_at: 2026-06-10
tags: [venmo, contacts, api, workflow]
---

# Like Venmo Transactions Involving Relatives

## Overview

This skill automates liking all Venmo transactions from a specific date that involve any of the user's relatives, as identified in the phone's contacts. It uses only app APIs and processes all paginated results.

## When To Use

- You need to like all Venmo transactions from a specific date involving any of the user's relatives (e.g., siblings, parents) as found in the phone's contacts.
- You must use only app APIs (not OS modules or external packages) and process all paginated results.

## Workflow

1. Retrieve the user's Venmo and phone app passwords from the supervisor app using the appropriate API.
2. Log in to the Venmo app using the user's email and Venmo password to obtain an access token.
3. Log in to the phone app using the user's phone number and phone password to obtain an access token.
4. Retrieve all contacts with the desired relationship (e.g., 'sibling') using the phone app's contacts API, paging through all results.
5. Get the current date and time from the phone app's get_current_date_and_time API.
6. Compute the date range for the target day (e.g., 'yesterday' as 00:00:00 to 23:59:59).
7. Retrieve all pages of the Venmo social feed using the Venmo API, collecting all transactions.
8. Filter transactions to those created within the target date range where either the sender or receiver matches any of the user's relatives' emails.
9. For each matching transaction, call the Venmo like_transaction API with the transaction_id and access token.
10. After all transactions are liked, call the supervisor.complete_task API to mark the task as complete.

## Sources

- [trajectory summary](../../summaries/appworld__aw_react_train2_baseline__2a163ab_2.md)
- [normalized JSON](benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/2a163ab_2.json)
