---
type: cluster
slug: iterate-all-pages-paginated-apis
title: Iterate through all pages in paginated APIs
tags: [pagination, api, completeness]
verified_at: 2026-06-10
members:
  - id: 04d27d43d285
    link: process-all-pages-in-paginated-apis__04d27d43d285.md
  - id: 0e301c1dc9a1
    link: process-all-pages-in-paginated-apis__0e301c1dc9a1.md
priority: high
---

# Iterate through all pages in paginated APIs

When working with APIs that paginate results, it is essential to retrieve all available data by looping through every page. Stopping at the first page or failing to increment the page index can result in incomplete data and missed results. These guidelines stress the importance of aggregating results across all pages for completeness.

## Takeaway

Always iterate through all pages of a paginated API by incrementing the page index until no more results are returned. Aggregate results across all pages to ensure you do not miss any relevant data.

## Members

These guidelines are kept as separate pages for full provenance back to their source trajectories. The cluster references them; nothing is moved or merged.

### [Process all pages in paginated APIs](process-all-pages-in-paginated-apis__04d27d43d285.md)

- **id:** `04d27d43d285`
- **trigger:** Whenever you call an API that supports pagination (e.g., show_received_payment_requests, search_contacts).
- **source:** [appworld__aw_r](../summaries/appworld__aw_react_train2_baseline__6ea6792_3.md)

> When retrieving results from a paginated API, always loop through all pages using the page_index and page_limit parameters until no more results are returned. Aggregate results across all pages to ensure completeness.

### [Process all pages in paginated APIs](process-all-pages-in-paginated-apis__0e301c1dc9a1.md)

- **id:** `0e301c1dc9a1`
- **trigger:** Whenever you need to retrieve a complete list of items from a paginated API endpoint.
- **source:** [appworld__aw_r](../summaries/appworld__aw_react_train2_baseline__2a163ab_2.md)

> When using paginated APIs, always iterate through all pages by incrementing the page_index until no more results are returned. Do not stop at the first page, as this may miss relevant data.
