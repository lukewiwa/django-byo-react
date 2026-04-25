/**
 * Core parser for the django-byo-react template tag output.
 *
 * The Django side renders:
 *   <script id="{scriptId}" type="application/json">{...}</script>
 *   <div id="{elementId}"
 *        data-script-id="{scriptId}"
 *        [data-component-name="{name}"]
 *        [class="..."]></div>
 *
 * This module reads those props back out of the DOM in a type-safe way.
 */

export class ByoReactError extends Error {
  override name = "ByoReactError";
}

/**
 * A validator turns an `unknown` JSON-parsed value into the desired prop
 * type, throwing if the shape is wrong. Compatible with `zod.parse`,
 * `valibot.parse`, hand-rolled guards, etc.
 */
export type Validator<T> = (value: unknown) => T;

export interface ByoReactContainer<T = unknown> {
  /** The container element React should mount into. */
  container: HTMLElement;
  /** The associated `<script type="application/json">` element. */
  script: HTMLScriptElement;
  /** The parsed props from the script tag. */
  props: T;
  /** The `data-component-name` attribute, if present. */
  componentName: string | undefined;
}

const SCRIPT_ID_ATTR = "data-script-id";
const COMPONENT_NAME_ATTR = "data-component-name";

function getDoc(root: ParentNode | Document | undefined): Document {
  if (root && "ownerDocument" in root && root.ownerDocument) {
    return root.ownerDocument;
  }
  if (typeof document === "undefined") {
    throw new ByoReactError(
      "No `document` available. Pass a `root` explicitly when running outside the browser.",
    );
  }
  return document;
}

function readJson(script: HTMLScriptElement): unknown {
  const text = script.textContent ?? "";
  try {
    return JSON.parse(text === "" ? "null" : text);
  } catch (err) {
    const reason = err instanceof Error ? err.message : String(err);
    throw new ByoReactError(
      `Failed to parse JSON from <script id="${script.id}">: ${reason}`,
    );
  }
}

function resolveScript(
  container: HTMLElement,
  doc: Document,
): HTMLScriptElement {
  const scriptId = container.getAttribute(SCRIPT_ID_ATTR);
  if (!scriptId) {
    throw new ByoReactError(
      `Container <${container.tagName.toLowerCase()} id="${container.id}"> is missing a ${SCRIPT_ID_ATTR} attribute. Did you render it with {% byo_react %}?`,
    );
  }
  const script = doc.getElementById(scriptId);
  if (!script) {
    throw new ByoReactError(
      `No <script id="${scriptId}"> found for container "${container.id}".`,
    );
  }
  if (!(script instanceof HTMLScriptElement)) {
    throw new ByoReactError(
      `Element with id "${scriptId}" is not a <script>.`,
    );
  }
  return script;
}

/**
 * Parse the props for a known container element.
 *
 * Pass a `validate` function (e.g. `zodSchema.parse`) to get a runtime-checked
 * `T`. Without one, the return is unsafely cast to `T` — use the generic only
 * when you trust the producer.
 */
export function parseProps<T = unknown>(
  container: HTMLElement,
  validate?: Validator<T>,
): T {
  const doc = getDoc(container);
  const script = resolveScript(container, doc);
  const raw = readJson(script);
  return validate ? validate(raw) : (raw as T);
}

export interface FindOptions {
  /** Where to search. Defaults to the global `document`. */
  root?: ParentNode;
}

/**
 * Look up a container by its `id` and parse its props.
 *
 * Throws `ByoReactError` if the element or its associated script is missing.
 */
export function parsePropsById<T = unknown>(
  id: string,
  validate?: Validator<T>,
  options: FindOptions = {},
): ByoReactContainer<T> {
  const doc = getDoc(options.root);
  const root: ParentNode = options.root ?? doc;
  const container =
    "getElementById" in root && typeof root.getElementById === "function"
      ? (root as Document).getElementById(id)
      : root.querySelector(`#${cssEscape(id)}`);
  if (!container) {
    throw new ByoReactError(`No element with id "${id}" was found.`);
  }
  if (!(container instanceof HTMLElement)) {
    throw new ByoReactError(`Element with id "${id}" is not an HTMLElement.`);
  }
  const script = resolveScript(container, doc);
  const props = (validate ?? identity)(readJson(script)) as T;
  return {
    container,
    script,
    props,
    componentName: container.getAttribute(COMPONENT_NAME_ATTR) ?? undefined,
  };
}

/**
 * Find every container rendered with `component_name="<name>"` and parse
 * its props. The validator (when provided) is applied per-element so a single
 * bad element does not silently corrupt the rest.
 */
export function parsePropsByComponentName<T = unknown>(
  name: string,
  validate?: Validator<T>,
  options: FindOptions = {},
): Array<ByoReactContainer<T>> {
  const doc = getDoc(options.root);
  const root: ParentNode = options.root ?? doc;
  const selector = `[${COMPONENT_NAME_ATTR}="${cssEscape(name)}"]`;
  const elements = root.querySelectorAll<HTMLElement>(selector);
  const out: Array<ByoReactContainer<T>> = [];
  elements.forEach((container) => {
    const script = resolveScript(container, doc);
    const props = (validate ?? identity)(readJson(script)) as T;
    out.push({
      container,
      script,
      props,
      componentName: container.getAttribute(COMPONENT_NAME_ATTR) ?? undefined,
    });
  });
  return out;
}

function identity(value: unknown): unknown {
  return value;
}

function cssEscape(value: string): string {
  if (typeof CSS !== "undefined" && typeof CSS.escape === "function") {
    return CSS.escape(value);
  }
  return value.replace(/["\\\]]/g, "\\$&");
}
