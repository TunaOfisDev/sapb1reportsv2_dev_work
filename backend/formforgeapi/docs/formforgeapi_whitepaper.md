```md
<!-- backend/formforgeapi/docs/formforgeapi_whitepaper.md -->
# FormForgeAPI White-Paper v1.0 — Architectural & Technical Deep-Dive  
Selim Koçak · August 2025

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)  
2. [System Vision & Use-Cases](#2-system-vision--use-cases)  
3. [Macro-Architecture](#3-macro-architecture)  
4. [Backend Domain Model](#4-backend-domain-model)  
5. [REST API Specification](#5-rest-api-specification)  
6. [Business Rules & Transactions](#6-business-rules--transactions)  
7. [Frontend Logical Architecture](#7-frontend-logical-architecture)  
8. [Drag-and-Drop (DnD) Contract](#8-drag-and-drop-dnd-contract)  
9. [Validation & Security](#9-validation--security)  
10. [Performance & Scalability](#10-performance--scalability)  
11. [DevOps & Deployment](#11-devops--deployment)  
12. [Testing Strategy](#12-testing-strategy)  
13. [Road-Map & Future-Work](#13-road-map--future-work)

---

## 1. Executive Summary
FormForgeAPI is a **low-code form-builder & data-collection platform** for SAP B1 reporting suite.  
*Backend:* Django 3.3 + DRF 3.16, PostgreSQL 15, Redis 7 (task queue / cache).  
*Frontend:* React 18, react-hook-form 7, react-beautiful-dnd 13, react-table 7.  
The module offers:  
* **Visual builder** with Palette → Canvas → Properties Drawer UX.  
* **Nested grid layout** (section › row › field).  
* **Atomic field update** & order mutation endpoint.  
* **Submission engine** with nested create (values []).  
* **White-label theming** via BEM-scoped CSS Modules.

---

## 2. System Vision & Use-Cases
| Actor | UC-ID | Description |
|-------|-------|-------------|
| Form designer | UC-01 | Compose dynamic form schema with drag-and-drop. |
| Form designer | UC-02 | Publish / unpublish draft; versioning (future). |
| End-user | UC-03 | Fill active form; server-side validation & submission. |
| Analyst | UC-04 | Export submissions as CSV/PDF. |
| Integrator | UC-05 | Pull schema & submissions via REST for BI pipelines. |

---

## 3. Macro-Architecture
```

┌──────────────┐      REST/JSON       ┌──────────────┐
│  React SPA   │  ──────────────────► │  Django DRF  │
│ (FormForge)  │ ◄──────────────────  │   Backend    │
└──────────────┘   WebSocket\* (v2)    └─────┬────────┘
▲                                     │
│ Redis pub/sub (Celery)              │
▼                                     ▼
┌─────────────────────────────┐     ┌──────────────────┐
│   Async Workers (Celery)    │     │ PostgreSQL 15 DB │
└─────────────────────────────┘     └──────────────────┘

````
*WS channel reserved for real-time collaboration roadmap.*

---

## 4. Backend Domain Model
```mermaid
classDiagram
  Form "1" --> "many" FormField : fields
  Form "1" --> "many" FormSubmission : submissions
  FormSubmission "1" --> "many" SubmissionValue : values
  Form o-- Department : department
  FormField : +Char label
  FormField : +Enum field_type
  FormField : +Bool is_required
  FormField : +Bool is_master
  FormField : +Int order
````

| Table              | PK | Key Columns                             | Indexes                      |
| ------------------ | -- | --------------------------------------- | ---------------------------- |
| `department`       | id | name (U)                                |                              |
| `form`             | id | department\_id (FK), created\_by\_id    | idx\_dept, idx\_owner        |
| `form_field`       | id | form\_id(FK), order                     | idx\_order (form\_id, order) |
| `form_submission`  | id | form\_id(FK), created\_by\_id           | idx\_form, idx\_owner        |
| `submission_value` | id | submission\_id(FK), form\_field\_id(FK) | idx\_field                   |

*All FK cascades are **`PROTECT`** except `submission_value` (`CASCADE`).*

---

## 5. REST API Specification

| Verb   | URL                                              | Body                   | Notes                     |
| ------ | ------------------------------------------------ | ---------------------- | ------------------------- |
| `GET`  | `/api/v2/formforgeapi/forms/`                    | –                      | Pagination, search `?q=`. |
| `POST` | `/api/v2/formforgeapi/forms/`                    | `{title, ...}`         | `created_by` auto.        |
| `POST` | `/api/v2/formforgeapi/form_fields/`              | `{form, label, ...}`   |                           |
| `POST` | `/api/v2/formforgeapi/form_fields/update_order/` | `[{id, order}]`        | Bulk atomic.              |
| `POST` | `/api/v2/formforgeapi/form_submissions/`         | `{form, values:[...]}` | Nested serializer.        |

### 5.1 Update-Order Endpoint

```python
@action(detail=False, methods=["post"])
def update_order(self, request):
    with transaction.atomic():
        for item in request.data:
            FormField.objects.filter(pk=item["id"])\
                    .update(order=item["order"])
    return Response(status=204)
```

---

## 6. Business Rules & Transactions

1. **Label uniqueness** *within a form* enforced at service layer.
2. **Options allowed** only for `select|radio|checkbox`.
3. **Master field** (`is_master`) max 1 per form (validated pre-save).
4. Submission reject on:

   * missing required values
   * field count mismatch (`FORM_REV_HASH` header to prevent stale schema)
5. Bulk create of values via `bulk_create()` inside the same `atomic()`.

---

## 7. Frontend Logical Architecture

```
/hooks
   ├─ useFormForgeDesigner.js  ← state, DnD, API I/O
   ├─ useFormForgePreview.js
/components
   ├─ palette/
   ├─ canvas/
   ├─ properties/
   └─ reusable/
```

*“Brain / Limb” split enforced; page-level screens render only data from hooks.*

---

## 8. Drag-and-Drop (DnD) Contract

| Type    | `draggableId`          | `droppableId`       | Handler                         |
| ------- | ---------------------- | ------------------- | ------------------------------- |
| Palette | `palette-${fieldType}` | `"palette"`         | onDragEnd→`addFieldFromPalette` |
| Field   | `${fieldId}`           | `row-{sIdx}-{rIdx}` | onDragEnd→`moveField`           |

---

## 9. Validation & Security

* **JWT Auth** via Axios interceptor; automatic refresh.
* CSRF exempt on API (token-only SPA).
* Per-object permissions: user must own the form to mutate schema.
* **Rate-limit** `/form_submissions/` 30 req/min per IP via `django-ratelimit`.
* Input sanitized with `bleach` for textarea HTML (future rich-text).

---

## 10. Performance & Scalability

| Layer | Optimisation                                                              |
| ----- | ------------------------------------------------------------------------- |
| DB    | composite index `(form_id, order)` speeds builder load (O(n log n)→O(n)). |
| API   | `prefetch_related("fields")` (Form list) – reduces N+1.                   |
| Front | CSS Modules (tree-shakable), code-splitting by `react-lazy`.              |
| Infra | Gunicorn + Uvicorn workers (`async` for WebSocket roadmap).               |

---

## 11. DevOps & Deployment

* **CI:** GitHub Actions → lint + pytest + build.
* **CD:** Docker multi-stage: `backend` (gunicorn) + `frontend` (Nginx).
* `.env` overrides via `docker-compose`, secrets injected at runtime (Vault).
* Observability: Prometheus metrics (`django-prometheus`), Loki logs, Grafana dashboards.

---

## 12. Testing Strategy

| Level          | Tool                                  | Coverage                 |
| -------------- | ------------------------------------- | ------------------------ |
| Unit (backend) | `pytest` + `pytest-django`            | ≥ 90 % lines             |
| Contract       | `drf-spectacular` schema diff + Dredd | 100 % endpoints          |
| E2E (front)    | Cypress                               | builder flow, fill flow  |
| Load test      | Locust                                | 500 VU, avg P95 < 250 ms |

---

## 13. Road-Map & Future-Work

* **v1.1** – real-time collaborative design (Y-js CRDT + WS).
* **v1.2** – form versioning & rollback; submission linked to revision.
* **v1.3** – conditional logic (“show if”, “calc field”).
* **v2.0** – server-side PDF render (WeasyPrint) & public share links.

---

© 2025 Selim Koçak · All rights reserved

```
::contentReference[oaicite:0]{index=0}
```
