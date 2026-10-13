# Variables, resources and events

Pages can hold state and react to visitors without code. Three pieces work together.

## Page variables

A variable has a name, a type and a starting value. Define them in the **Data** panel of the left sidebar.

- Show a variable in any text with `{{ variableName }}`.
- Use it in a **Show when** rule, such as `menuOpen` or `cartCount > 0`.
- Change it from an event's script with `variableName.value = …`.
- A repeater can write its row count into a variable, so a heading can say how many products are listed.

## Resources

A resource is named data the page loads: a list of records, one record, or an API call. Set its fields, filters, sort and limit, a transform for the answer, and what happens on success or failure. Bind elements and repeaters to it by name, and reload it from an event.

## Events

Select an element and open its events. Each event runs one action.

**Events:** click, double click, change, input, focus, blur, submit, key down, key up, mouse enter, mouse leave, and scroll of the page.

**Actions:**

- **Run a script.**
- **Call an API**, with separate handling for success and error.
- **Insert a document** of a record type.
- **Navigate** to a page or address, or **open a web page**.
- **Toggle an accordion** or **toggle the mobile menu**.
- **Show a toast** or **show an alert**.

**Call API** can call a page resource or any allowed server method, with parameters taken from variables and fields, and then show a message or run a script for success and for failure.

Scripts get the page's variables, the route (for example `route.query.category`), the repeater row they sit in (`dataItem`) and the event's own values. The scroll event also gets the scroll position, so a header can change as the visitor scrolls.

## Show when

Any element can carry a **Show when** expression. It is checked on the published page and on the server, so hidden blocks never flash. The simpler **Visibility** rule in Settings shows an element only when a data field is set or empty, explained in plain words. While you edit, a hidden element appears when you select it in Layers.

## Where this runs

Variables, resources and events run on the published page and in the builder's preview. Events do not fire while you are editing on the canvas.
