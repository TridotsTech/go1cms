# Portal data sources

A portal page never names a record type directly. It names a **data source**: an approved, per-website definition that decides on the server what members may see and change.

## What a data source decides

| Setting | Choices |
| --- | --- |
| Who may read | Everyone, signed-in members, or chosen portal roles |
| Which records | All, the member's own, records in their account field, their linked record (Customer, Supplier, Employee and so on), or records linked to it |
| Which fields | Only the fields listed leave the server |
| What may change | Create, edit and delete, each switched on separately, with the fields that may be written and the roles that may edit |
| Automatic values | Values set on every record a member creates |
| Order and filters | Default sort and fixed filters |
| Detail page | The address that shows one record |

## Actions

A data source can offer buttons on a record, such as **Mark as solved**, **Reopen**, **Accept quote**, **Approve** or **Ask for changes**. Each action sets field values, appears only in the right state, can be limited to roles, and can require a comment.

## Ready-made sources

Presets exist for common jobs and are offered only when their record type exists on the site: support tickets, sales orders, invoices, quotations, deliveries, projects, tasks, timesheets, purchase orders, requests for quotation, supplier quotations, leads, appointments, leave, attendance and payslips.

## Payments

A data source can show **Pay now** on a record, with the amount always read from the record, never from the browser (see [Bookings, memberships and payments](../bookings-and-memberships)).

## Notifications

Rules on a data source notify the member, the record owner, a portal role or the editors by bell, email or SMS when a record is created, updated, deleted, acted on, or reaches a field value.
