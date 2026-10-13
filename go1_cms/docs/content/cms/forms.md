# Forms

Two ways to collect input.

## Native inputs

**Input**, **Textarea**, **Select** and **Checkbox** are real form controls bound to page variables. Combine them with a **Button** whose click runs a **Call API** or **Submit** action. Validation (required, pattern, min and max) lives in the inspector. Select options can be static or loaded from an API.

## Form Builder forms

The **Form** element renders a form designed in Form Builder and submits to the DocType you chose, for example a Contact Enquiry or a Lead. Fields, required flags and success messages come from the form; the page only decides where it sits and how it looks.

## After submit

Actions on the form's submit event can navigate to a thank-you page, show a toast, or set a variable that reveals a message. Submissions appear under **Forms** in the admin with a per-form list and export.

## Spam and rate limits

Guest submissions are rate-limited per address, and required-field checks run on the server as well as in the browser.
