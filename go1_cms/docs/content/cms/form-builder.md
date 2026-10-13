# Form builder

**Forms** builds public forms: contact, quote requests, bookings, job applications, surveys and more. A form saves each answer as a record and lands in the form inbox.

## Starting a form

Press **New form** and pick a template from 13 groups, including contact and enquiries, sales and quotes, bookings and appointments, events, feedback and surveys, jobs, education, health, real estate, restaurants and travel, shop and orders, nonprofit and community, and newsletters. Or start blank.

## Questions

| Type | Use |
| --- | --- |
| Short answer, Long answer | Text |
| Email, Phone, Number, Website link | Checked formats |
| Dropdown, Multiple choice, Checkboxes | Choices from a list |
| Tick box | Agree or confirm |
| Star rating | 1 to 5 stars |
| Date, Time | When |
| Section title | Splits a long form into parts |

Each question has a label, a placeholder, help text, required and hidden flags and a width, so two short questions can share a row. Add a **Captcha** to ask a small sum the server checks before it accepts the answer.

## Where answers go

Connect the form to a record type, such as Contact Enquiry, Lead or any other DocType. The questions can be filled from that record type's real fields. Every accepted answer creates that record and an inbox entry.

## Look

Forms take the website's theme tokens: colours, fonts and corners match the page they sit on. The form page at `/forms/<address>` has an optional banner with heading, text and image.

## After submit

Show a thank-you message or send the visitor to another page.

## Putting a form on a page

Add the **Form** element and pick the form. It renders inside the page's own design, on the canvas and on the published site.
