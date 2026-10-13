# Query builder

**Query builder** saves queries that collections and pages can read. Use it when a list needs data a simple filter cannot express.

## Two ways to write a query

- **Visual**: pick a record type, the fields, filters, sorting, grouping, totals and a row limit. Visual queries run as the person viewing them, so their own permissions apply.
- **SQL**: write a read-only `SELECT` statement. SQL is for people with the role that allows it, both to write and to run. Every statement is checked again each time it runs, and anything that is not a single read is refused.

## Running and saving

Run a query to see the rows, how long it took and the statement that ran. Save it with a name, a description, a reference record type and a limit, or save a copy under a new name. Mark a query public to let others use it.

## Using a query on a page

Create a collection in **Custom** mode and pick the saved query. Its columns become the fields a repeater can bind to (see [Collections](../collections)).

Old visual queries from earlier versions open read-only, with a one-click conversion.
