---
type: section-index
section: guidelines
verified_at: 2026-06-10
count: 13
atomic: 10
clusters: 3
---

# Guidelines

Atomic, trigger-tagged lessons plus aggregator **cluster pages** that group related variants. Cluster pages have the suffix `__cluster.md` and are recall-preferred — when a cluster and its members both match a query, the cluster wins. Members carry a `superseded_by:` field pointing at their cluster.

## Clusters (prefer these first)

- **[Always retrieve credentials via supervisor API](supervisor-api-credentials__cluster.md)** `cluster:supervisor-api-credentials` — `tags: credentials, supervisor-api, authentication` (2 members)
- **[Iterate through all pages in paginated APIs](iterate-all-pages-paginated-apis__cluster.md)** `cluster:iterate-all-pages-paginated-apis` — `tags: pagination, api, completeness` (2 members)
- **[Use contacts API for relationship-based filtering](contacts-api-relationship-filtering__cluster.md)** `cluster:contacts-api-relationship-filtering` — `tags: contacts, relationships, filtering` (2 members)

## Atomic guidelines, alphabetical

- **[Always retrieve credentials via supervisor API](always-retrieve-credentials-via__ca7497056794.md)** `ca7497056794` [→ cluster: supervisor-api-credentials](supervisor-api-credentials__cluster.md)
  - When authentication is required for an app, retrieve the relevant credentials (such as passwords) using the supervisor app's API rather…
- **[Filter and act on API data using runtime logic](filter-and-act-on-api-data-using__e56a8dc4874d.md)** `e56a8dc4874d`
  - After retrieving data from APIs (such as social feeds or transactions), apply runtime filtering logic (e.g., by date or participant) before…
- **[Filter entities using contact relationships](filter-entities-using-contact__16f6835b55ef.md)** `16f6835b55ef` [→ cluster: contacts-api-relationship-filtering](contacts-api-relationship-filtering__cluster.md)
  - To identify users who are friends or coworkers, retrieve your contacts and filter by the 'relationships' field. Use this filtered set to…
- **[Inspect API documentation before calling](inspect-api-documentation-before-calling__69dd6c0e2fbd.md)** `69dd6c0e2fbd`
  - Before invoking any API, especially for unfamiliar endpoints, call the API documentation endpoint (e.g., show_api_doc or…
- **[Obtain current date from environment API](obtain-current-date-from-environment-api__e40f389adcaa.md)** `e40f389adcaa`
  - Always obtain the current date and time from the environment or device API (such as get_current_date_and_time) rather than relying on your…
- **[Process all pages in paginated APIs](process-all-pages-in-paginated-apis__04d27d43d285.md)** `04d27d43d285` [→ cluster: iterate-all-pages-paginated-apis](iterate-all-pages-paginated-apis__cluster.md)
  - When retrieving results from a paginated API, always loop through all pages using the page_index and page_limit parameters until no more…
- **[Process all pages in paginated APIs](process-all-pages-in-paginated-apis__0e301c1dc9a1.md)** `0e301c1dc9a1` [→ cluster: iterate-all-pages-paginated-apis](iterate-all-pages-paginated-apis__cluster.md)
  - When using paginated APIs, always iterate through all pages by incrementing the page_index until no more results are returned. Do not stop…
- **[Retrieve credentials via supervisor API](retrieve-credentials-via-supervisor-api__03487fdd6432.md)** `03487fdd6432` [→ cluster: supervisor-api-credentials](supervisor-api-credentials__cluster.md)
  - Always obtain app credentials such as passwords by calling the supervisor app's credential retrieval API (e.g., show_account_passwords)…
- **[Use contacts API for relationship queries](use-contacts-api-for-relationship__71262af0cdc7.md)** `71262af0cdc7` [→ cluster: contacts-api-relationship-filtering](contacts-api-relationship-filtering__cluster.md)
  - To identify users with a specific relationship (such as siblings), use the phone app's contacts API with the appropriate relationship…
- **[Use only app APIs for app interaction](use-only-app-apis-for-app-interaction__d99bba5cbfea.md)** `d99bba5cbfea`
  - When interacting with an app, use only the provided app APIs rather than corresponding Python packages or OS-level modules. For example,…

## By tag

### `api`

- [Inspect API documentation before calling](inspect-api-documentation-before-calling__69dd6c0e2fbd.md) `69dd6c0e2fbd`
- [Process all pages in paginated APIs](process-all-pages-in-paginated-apis__04d27d43d285.md) `04d27d43d285`
- [Use only app APIs for app interaction](use-only-app-apis-for-app-interaction__d99bba5cbfea.md) `d99bba5cbfea`

### `api-usage`

- [Always retrieve credentials via supervisor API](always-retrieve-credentials-via__ca7497056794.md) `ca7497056794`
- [Filter and act on API data using runtime logic](filter-and-act-on-api-data-using__e56a8dc4874d.md) `e56a8dc4874d`
- [Obtain current date from environment API](obtain-current-date-from-environment-api__e40f389adcaa.md) `e40f389adcaa`
- [Process all pages in paginated APIs](process-all-pages-in-paginated-apis__0e301c1dc9a1.md) `0e301c1dc9a1`
- [Use contacts API for relationship queries](use-contacts-api-for-relationship__71262af0cdc7.md) `71262af0cdc7`

### `contacts`

- [Filter entities using contact relationships](filter-entities-using-contact__16f6835b55ef.md) `16f6835b55ef`
- [Use contacts API for relationship queries](use-contacts-api-for-relationship__71262af0cdc7.md) `71262af0cdc7`

### `credentials`

- [Always retrieve credentials via supervisor API](always-retrieve-credentials-via__ca7497056794.md) `ca7497056794`
- [Retrieve credentials via supervisor API](retrieve-credentials-via-supervisor-api__03487fdd6432.md) `03487fdd6432`

### `pagination`

- [Process all pages in paginated APIs](process-all-pages-in-paginated-apis__04d27d43d285.md) `04d27d43d285`
- [Process all pages in paginated APIs](process-all-pages-in-paginated-apis__0e301c1dc9a1.md) `0e301c1dc9a1`

### `relationships`

- [Filter entities using contact relationships](filter-entities-using-contact__16f6835b55ef.md) `16f6835b55ef`
- [Use contacts API for relationship queries](use-contacts-api-for-relationship__71262af0cdc7.md) `71262af0cdc7`

### `security`

- [Always retrieve credentials via supervisor API](always-retrieve-credentials-via__ca7497056794.md) `ca7497056794`
- [Retrieve credentials via supervisor API](retrieve-credentials-via-supervisor-api__03487fdd6432.md) `03487fdd6432`


## Recall roll-up

Cross-summary tally of `recalled_guidelines:` blocks. Rows are alphabetical by guideline title. A row of zeros means the guideline has been contributed by a session but never recalled by another.

| Guideline | Total | followed | ignored | contradicted | harmful |
|-----------|------:|---------:|--------:|-------------:|--------:|
| [Always retrieve credentials via supervisor API](always-retrieve-credentials-via__ca7497056794.md) | 0 | 0 | 0 | 0 | 0 |
| [Filter and act on API data using runtime logic](filter-and-act-on-api-data-using__e56a8dc4874d.md) | 0 | 0 | 0 | 0 | 0 |
| [Filter entities using contact relationships](filter-entities-using-contact__16f6835b55ef.md) | 0 | 0 | 0 | 0 | 0 |
| [Inspect API documentation before calling](inspect-api-documentation-before-calling__69dd6c0e2fbd.md) | 0 | 0 | 0 | 0 | 0 |
| [Obtain current date from environment API](obtain-current-date-from-environment-api__e40f389adcaa.md) | 0 | 0 | 0 | 0 | 0 |
| [Process all pages in paginated APIs](process-all-pages-in-paginated-apis__04d27d43d285.md) | 0 | 0 | 0 | 0 | 0 |
| [Process all pages in paginated APIs](process-all-pages-in-paginated-apis__0e301c1dc9a1.md) | 0 | 0 | 0 | 0 | 0 |
| [Retrieve credentials via supervisor API](retrieve-credentials-via-supervisor-api__03487fdd6432.md) | 0 | 0 | 0 | 0 | 0 |
| [Use contacts API for relationship queries](use-contacts-api-for-relationship__71262af0cdc7.md) | 0 | 0 | 0 | 0 | 0 |
| [Use only app APIs for app interaction](use-only-app-apis-for-app-interaction__d99bba5cbfea.md) | 0 | 0 | 0 | 0 | 0 |

## Pages, by priority

Unified roll-up across clusters + atomic guidelines. Priority is computed each catalog run from recall counts and cluster membership (not authored). Rows sort by tier (`high` → `disputed` → `weak` → `normal` → `low` → `unvalidated`), then alphabetical within tier.

| Title | Kind | Priority | Trigger | Tags | Cluster | Recall (T / f / i / c / h) | Verified at |
|-------|------|----------|---------|------|---------|---------------------------:|-------------|
| [Always retrieve credentials via supervisor API](supervisor-api-credentials__cluster.md) | cluster | **high** | — | credentials, supervisor-api, authentication | — | — | 2026-06-10 |
| [Iterate through all pages in paginated APIs](iterate-all-pages-paginated-apis__cluster.md) | cluster | **high** | — | pagination, api, completeness | — | — | 2026-06-10 |
| [Use contacts API for relationship-based filtering](contacts-api-relationship-filtering__cluster.md) | cluster | **high** | — | contacts, relationships, filtering | — | — | 2026-06-10 |
| [Always retrieve credentials via supervisor API](always-retrieve-credentials-via__ca7497056794.md) | atomic | **low** | When you need to log in to any connected app and require a password or other … | credentials, security, api-usage | supervisor-api-credentials | 0 / 0 / 0 / 0 / 0 | 2026-06-10 |
| [Filter entities using contact relationships](filter-entities-using-contact__16f6835b55ef.md) | atomic | **low** | When a task requires acting only on items related to friends, coworkers, or o… | contacts, filtering, relationships | contacts-api-relationship-filtering | 0 / 0 / 0 / 0 / 0 | 2026-06-10 |
| [Process all pages in paginated APIs](process-all-pages-in-paginated-apis__04d27d43d285.md) | atomic | **low** | Whenever you call an API that supports pagination (e.g., show_received_paymen… | pagination, api, data-integrity | iterate-all-pages-paginated-apis | 0 / 0 / 0 / 0 / 0 | 2026-06-10 |
| [Process all pages in paginated APIs](process-all-pages-in-paginated-apis__0e301c1dc9a1.md) | atomic | **low** | Whenever you need to retrieve a complete list of items from a paginated API e… | pagination, api-usage, data-completeness | iterate-all-pages-paginated-apis | 0 / 0 / 0 / 0 / 0 | 2026-06-10 |
| [Retrieve credentials via supervisor API](retrieve-credentials-via-supervisor-api__03487fdd6432.md) | atomic | **low** | When you need to log in to any app and require a password or other credential. | credentials, supervisor, security | supervisor-api-credentials | 0 / 0 / 0 / 0 / 0 | 2026-06-10 |
| [Use contacts API for relationship queries](use-contacts-api-for-relationship__71262af0cdc7.md) | atomic | **low** | When you need to find users with a particular relationship (e.g., sibling, pa… | contacts, relationships, api-usage | contacts-api-relationship-filtering | 0 / 0 / 0 / 0 / 0 | 2026-06-10 |
| [Filter and act on API data using runtime logic](filter-and-act-on-api-data-using__e56a8dc4874d.md) | atomic | **unvalidated** | When you need to perform actions on a subset of data retrieved from an API, b… | data-filtering, api-usage, runtime-logic | — | 0 / 0 / 0 / 0 / 0 | 2026-06-10 |
| [Inspect API documentation before calling](inspect-api-documentation-before-calling__69dd6c0e2fbd.md) | atomic | **unvalidated** | When preparing to call an API you have not used before or when the API's para… | api, documentation, reliability | — | 0 / 0 / 0 / 0 / 0 | 2026-06-10 |
| [Obtain current date from environment API](obtain-current-date-from-environment-api__e40f389adcaa.md) | atomic | **unvalidated** | When you need to compute time ranges (e.g., 'yesterday') or respond to time-s… | datetime, environment, api-usage | — | 0 / 0 / 0 / 0 / 0 | 2026-06-10 |
| [Use only app APIs for app interaction](use-only-app-apis-for-app-interaction__d99bba5cbfea.md) | atomic | **unvalidated** | Whenever you need to perform actions within an app that exposes its own API s… | api, app-integration, compatibility | — | 0 / 0 / 0 / 0 / 0 | 2026-06-10 |
