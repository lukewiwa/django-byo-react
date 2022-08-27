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

In the template that you want to install a react app load the tag and use it with the given `kwargs`. You can add extra props to the root react component by adding `kwargs` to the tag element. As long as is json serializable it can be included in the props.

```django
{% load byo_react %}

"{% byo_react id='react-app-id' className='w-100' showActive=True %}"
```

### Javascript/Typescript Example

The JS/TS side is left to the user as there are many ways in which one can create a react app. This leaves the most flexibility to integrate existing react apps and frameworks into a django page. The one important point is that the `id` is the variable that ties the backend to the frontend so keep this in sync.

Here is a typical example for a very basic app.

```typescript
import React, { FC } from "react";
import ReactDOM from 'react-dom/client';

// Example root component for a react app
const App: FC = (props) => <div {...props}></div>

const elementId = "react-element-id"
const scriptId = `${elementId}-props`

const container = document.getElementById(elementId)
if (!container) throw new Error(`Can't find element with id ${elementId}`);

// Extract props from the django json_script tag
const jsonContent = document.getElementById(scriptId)?.textContent;
if (!jsonContent)
  throw new Error(
    `No parsable json content found in element with id ${scriptId}`
  );

// props will be a dictionary containing the tag kwargs
// eg: The props constant will be an object with { showActive: true }
const props = JSON.parse(jsonContent);

const root = ReactDOM.createRoot(container)
root.render(<App {...props} />);
```