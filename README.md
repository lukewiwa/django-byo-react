# Django BYO React

A minimal template tag which creates a div element for React to bind to and a Django `json_script` which can be used to pass values from Django into the root React element as props. This library remains unopinionated about the React code by design since there are so many ways to create and maintain React apps.

## Usage

Install the app in `settings.py`

```python
INSTALLED_APPS = [
    "django_byo_react",
    ...
]
```

In the template that you want to install a react app load the tag and use it with the given `kwargs`. You can add extra props to the root react component by adding `kwargs` to the tag element. As long as is json serializable it can be included in the props. This library will give the json script a random uuid and add that as a data attribute `data-script-id` to the react app div. This can be used to access the data using javascript.

### Example using element id

If the react app is a one off embed we can use the `div` id to connect the backend to the frontend. In the following example we've used a simple string id `react-app-id`.

#### Django

```django
{% load byo_react %}

{% byo_react id="react-app-id" className="w-100" showActive=True %}
{% comment %}
    showActive is an extra keyword argument rendered in a html script tag
{% endcomment %}
```

This will render with the following HTML:

```html
<script id="<script-random-uuid>" type="application/json">{"showActive": true}</script>
<div id="react-app-id" data-script-id="<script-random-uuid>" class="w-100"></div>
```

##### Javascript/Typescript

The JS/TS side is left to the user as there are many ways in which one can create a react app. This leaves the most flexibility to integrate existing react apps and frameworks into a django page.

Here is a typical example for a very basic app using the div element id `react-app-id` to connect the root component from the backend render.

```typescript
import React, { FC } from "react";
import ReactDOM from "react-dom/client";

// Example root component for a react app
const App: FC = (props) => <div {...props}></div>

const elementId = "react-app-id"

const container = document.getElementById(elementId)
if (!container) throw new Error(`Can't find element with id ${elementId}`);

// Extract props from the django json_script tag
const jsonContent = document.getElementById(container.dataset?.scriptId)?.textContent;
if (!jsonContent) throw new Error("No associated script found");

// props will be a dictionary containing the tag kwargs
// eg: The props constant will be an object with { showActive: true }
const props = JSON.parse(jsonContent);

const root = ReactDOM.createRoot(container)
root.render(<App {...props} />);
```

### Example using component name

There is an optional `component_name` argument in the django `byo_react` template tag. This is intended for adding the react app root component name directly to the div data attribute so it can be used from the frontend. With the component name we can embed the same react app several times. This might be useful for a react app that needs to be used in several different elements on the same page such as form fields. Here's an example of how we might do that.

#### Django

```django
{% load byo_react %}

{% byo_react component_name="App" className="w-100" showActive=True %}
```

This will render with the following HTML:

```html
<script id="<script-random-uuid>" type="application/json">{"showActive": true}</script>
<div id="<div-random-uuid>" data-script-id="<script-random-uuid>" data-component-name="App" class="w-100"></div>
```

##### Javascript/Typescript

```typescript
import React, { FC } from "react";
import ReactDOM from "react-dom/client";

// Example root component for a react app
const App: FC = (props) => <div {...props}></div>

// Get all elements with data attribute `component-name` as "App"
document.querySelectorAll("[data-component-name='App']")).forEach(container => {
    // Extract props from the django json_script tag
    const jsonContent = document.getElementById(container.dataset?.scriptId)?.textContent;
    if (!jsonContent) throw new Error("No associated script found");

    // props will be a dictionary containing the tag kwargs
    // eg: The props constant will be an object with { showActive: true }
    const props = JSON.parse(jsonContent);

    const root = ReactDOM.createRoot(container)
    root.render(<App {...props} />);
})