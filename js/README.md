# django-byo-react (JS)

Type-safe parser and React mount helpers for the
[`django-byo-react`](https://pypi.org/project/django-byo-react/) Django
template tag.

The Django side renders a `<script type="application/json">` next to your
container `<div>`. This package reads those props back out of the DOM so you
don't have to wire it up by hand on every project — and gives you a typed
`Validator<T>` slot so you can verify the shape against your schema of choice
(zod, valibot, or a hand-rolled guard).

## Install

```bash
npm install django-byo-react
# react / react-dom are optional peer deps, only needed for the /react entry
npm install react react-dom
```

## Core: parse only

Zero dependencies. Works in any browser-ish environment that exposes
`document`.

```ts
import { parsePropsById } from "django-byo-react";

interface AppProps {
  showActive: boolean;
  name: string;
}

const { container, props } = parsePropsById<AppProps>("react-app-id");
//      ^? HTMLElement       ^? AppProps  (unsafe cast — see below)
```

### Type-safe with a validator

The generic-only form casts `unknown` to your type without checking. For real
safety, pass a `validate` function. Anything with a `(value: unknown) => T`
signature works — including `zod.parse`, `valibot.parse`, or a hand-written
guard.

```ts
import { z } from "zod";
import { parsePropsById } from "django-byo-react";

const AppPropsSchema = z.object({
  showActive: z.boolean(),
  name: z.string(),
});
type AppProps = z.infer<typeof AppPropsSchema>;

const { props } = parsePropsById("react-app-id", AppPropsSchema.parse);
//        ^? AppProps   — guaranteed by schema, throws ByoReactError on mismatch
```

### Multiple instances by `component_name`

```ts
import { parsePropsByComponentName } from "django-byo-react";

const fields = parsePropsByComponentName<{ value: number }>("CounterField");
fields.forEach(({ container, props }) => {
  // mount however you like
});
```

## React: mount helpers

```tsx
import { mountById } from "django-byo-react/react";

interface AppProps {
  showActive: boolean;
  name: string;
}

const App: React.FC<AppProps> = ({ name, showActive }) => (
  <div>{showActive ? `Hi ${name}` : null}</div>
);

mountById<AppProps>("react-app-id", App, { validate: AppPropsSchema.parse });
```

For the `component_name` pattern (one component, many embeds — e.g. form
fields):

```tsx
import { mountAllByComponentName } from "django-byo-react/react";

mountAllByComponentName("CounterField", CounterField, {
  validate: CounterPropsSchema.parse,
});
```

Each call returns a `MountedRoot` with `{ container, root, props, unmount }`,
so you can tear individual instances down on navigation.

## API

| Export                              | What it does                                         |
| ----------------------------------- | ---------------------------------------------------- |
| `parseProps(el, validate?)`         | Parse props for a container you already have.        |
| `parsePropsById(id, validate?)`     | Look up by id and parse.                             |
| `parsePropsByComponentName(name, …)`| Find all matches of `data-component-name`, parse each.|
| `ByoReactError`                     | Thrown for missing elements or bad JSON.             |
| `Validator<T>`                      | `(value: unknown) => T` — your schema's parser.      |
| `mount` / `mountById`               | Parse + `createRoot` + render in one call.           |
| `mountAllByComponentName`           | Same, but for every match of `component_name`.       |

## License

MIT
