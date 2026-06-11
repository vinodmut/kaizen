---
id: skill:accept-venmo-payment-requests-from-contacts
type: skill
name: accept-venmo-payment-requests-from-contacts
description: Approve all pending Venmo payment requests from users in your contacts list marked as friends or coworkers.
trigger: When you need to automatically accept all pending Venmo payment requests from people who are your friends or coworkers, as defined by your phone's contacts.
agent: appworld-react-code
sources:
  - benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/6ea6792_3.json
related_summary: summaries/appworld__aw_react_train2_baseline__6ea6792_3.md
verified_at: 2026-06-10
tags: [venmo, contacts, payment-requests, automation]
---

# Accept Venmo Payment Requests From Contacts

## Overview

This skill logs in to Venmo and your phone app, retrieves all pending Venmo payment requests, filters them to those sent by friends or coworkers in your contacts, and approves each one. Use this when you need to batch-accept payment requests from trusted contacts.

## When To Use

- You need to approve all pending Venmo payment requests from your coworkers or friends.
- You want to automate accepting Venmo payment requests from people listed as friends or coworkers in your phone's contacts.

## Workflow

1. Retrieve your Venmo and phone app passwords using the supervisor app's show_account_passwords API.
2. Log in to Venmo using your email and Venmo password to obtain an access token (see venmo.login API).
3. Log in to the phone app using your phone number and phone password to obtain an access token (see phone.login API).
4. Retrieve all pending received Venmo payment requests, handling pagination (see venmo.show_received_payment_requests with status='pending').
5. Retrieve all contacts from your phone app, handling pagination (see phone.search_contacts).
6. Build a set of emails for contacts whose relationships include 'friend' or 'coworker'.
7. Filter the pending Venmo payment requests to those whose sender's email matches the set of friend/coworker contact emails.
8. For each filtered payment request, call venmo.approve_payment_request with the payment_request_id and your Venmo access token.
9. After all requests are approved, call supervisor.complete_task to mark the task as complete.

## Sources

- [trajectory summary](../../summaries/appworld__aw_react_train2_baseline__6ea6792_3.md)
- [normalized JSON](benchmark-data/appworld-agent-wiki/normalized/aw_react_train2_baseline/items/6ea6792_3.json)
