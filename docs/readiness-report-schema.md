---
layout: default
title: Readiness Report Schema
description: Stable schema for the IdM readiness report role.
---

{% raw %}

# Readiness Report Schema

Role: `eigenstate.ipa.idm_readiness_report`

Schema: `eigenstate.ipa/idm_readiness_report/v1`

The readiness report records checks that indicate whether IdM-backed automation
has the prerequisites it needs.

## Top-Level Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `schema` | string | Stable schema identifier. |
| `schema_version` | string | Schema version, currently `1.0`. |
| `role` | string | Always `idm_readiness_report`. |
| `generated_at_utc` | string | UTC timestamp supplied by the caller. |
| `site` | string | Site or environment label. |
| `context` | string | Human-readable report scope. |
| `read_only` | boolean | Always `true`. |
| `summary` | object | Counts by check state. |
| `checks` | array | Readiness check records. |

## Check Record

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Stable check identifier. |
| `title` | string | Human-readable check name. |
| `status` | string | `pass`, `warn`, `fail`, or `info`. |
| `severity` | string | Local severity label. |
| `evidence` | string | Safe evidence text. |
| `recommendation` | string | Next action or maintenance note. |

{% endraw %}
