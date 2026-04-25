import { afterEach, describe, expect, it } from "vitest";

import {
  ByoReactError,
  parseProps,
  parsePropsByComponentName,
  parsePropsById,
} from "../src/index.js";

afterEach(() => {
  document.body.innerHTML = "";
});

/** Mirror of the Django template output, for ergonomic test setup. */
function render({
  id,
  scriptId,
  json,
  componentName,
  className,
}: {
  id: string;
  scriptId: string;
  json: string;
  componentName?: string;
  className?: string;
}): HTMLElement {
  document.body.insertAdjacentHTML(
    "beforeend",
    `<script id="${scriptId}" type="application/json">${json}</script>` +
      `<div id="${id}" data-script-id="${scriptId}"` +
      (componentName ? ` data-component-name="${componentName}"` : "") +
      (className ? ` class="${className}"` : "") +
      `></div>`,
  );
  return document.getElementById(id) as HTMLElement;
}

describe("parseProps", () => {
  it("parses props from a container's linked script", () => {
    const container = render({
      id: "react-app",
      scriptId: "react-app-data",
      json: '{"showActive": true, "name": "Ada"}',
    });

    const props = parseProps(container);

    expect(props).toEqual({ showActive: true, name: "Ada" });
  });

  it("returns null for an empty json_script payload", () => {
    const container = render({
      id: "react-app",
      scriptId: "react-app-data",
      json: "",
    });

    expect(parseProps(container)).toBeNull();
  });

  it("applies a validator and yields the validated type", () => {
    interface AppProps {
      showActive: boolean;
      name: string;
    }
    const validate = (raw: unknown): AppProps => {
      if (
        typeof raw !== "object" ||
        raw === null ||
        typeof (raw as AppProps).showActive !== "boolean" ||
        typeof (raw as AppProps).name !== "string"
      ) {
        throw new Error("invalid props");
      }
      return raw as AppProps;
    };

    const container = render({
      id: "x",
      scriptId: "x-data",
      json: '{"showActive": true, "name": "Ada"}',
    });

    const props = parseProps(container, validate);
    expect(props.showActive).toBe(true);
    expect(props.name).toBe("Ada");
  });

  it("throws ByoReactError for malformed JSON", () => {
    const container = render({
      id: "x",
      scriptId: "x-data",
      json: "{not-json",
    });
    expect(() => parseProps(container)).toThrow(ByoReactError);
  });

  it("throws when data-script-id is missing", () => {
    document.body.insertAdjacentHTML("beforeend", '<div id="orphan"></div>');
    const orphan = document.getElementById("orphan") as HTMLElement;
    expect(() => parseProps(orphan)).toThrow(/data-script-id/);
  });

  it("throws when the linked script does not exist", () => {
    document.body.insertAdjacentHTML(
      "beforeend",
      '<div id="dangling" data-script-id="missing"></div>',
    );
    const el = document.getElementById("dangling") as HTMLElement;
    expect(() => parseProps(el)).toThrow(/No <script id="missing">/);
  });
});

describe("parsePropsById", () => {
  it("locates the container by id and returns metadata", () => {
    render({
      id: "hero",
      scriptId: "hero-data",
      json: '{"title": "Hello"}',
      componentName: "Hero",
      className: "w-100",
    });

    const result = parsePropsById<{ title: string }>("hero");
    expect(result.props.title).toBe("Hello");
    expect(result.componentName).toBe("Hero");
    expect(result.container.id).toBe("hero");
    expect(result.script.id).toBe("hero-data");
  });

  it("throws when no element matches", () => {
    expect(() => parsePropsById("nope")).toThrow(/No element with id "nope"/);
  });
});

describe("parsePropsByComponentName", () => {
  it("returns one entry per matching container", () => {
    render({
      id: "a",
      scriptId: "a-data",
      json: '{"value": 1}',
      componentName: "Counter",
    });
    render({
      id: "b",
      scriptId: "b-data",
      json: '{"value": 2}',
      componentName: "Counter",
    });
    render({
      id: "c",
      scriptId: "c-data",
      json: '{"value": 99}',
      componentName: "Other",
    });

    const results = parsePropsByComponentName<{ value: number }>("Counter");
    expect(results).toHaveLength(2);
    expect(results.map((r) => r.props.value).sort()).toEqual([1, 2]);
  });

  it("scopes the search to the provided root", () => {
    document.body.insertAdjacentHTML(
      "beforeend",
      '<section id="scope"></section>',
    );
    const scope = document.getElementById("scope") as HTMLElement;
    scope.insertAdjacentHTML(
      "beforeend",
      '<script id="s1" type="application/json">{"x": 1}</script>' +
        '<div id="d1" data-script-id="s1" data-component-name="App"></div>',
    );
    render({
      id: "outside",
      scriptId: "outside-data",
      json: '{"x": 2}',
      componentName: "App",
    });

    const inScope = parsePropsByComponentName("App", undefined, {
      root: scope,
    });
    expect(inScope).toHaveLength(1);
    expect((inScope[0]!.props as { x: number }).x).toBe(1);
  });

  it("escapes special characters in the component name selector", () => {
    document.body.insertAdjacentHTML(
      "beforeend",
      '<script id="s1" type="application/json">{"ok": true}</script>' +
        '<div id="d1" data-script-id="s1" data-component-name="My&quot;App"></div>',
    );
    const results = parsePropsByComponentName('My"App');
    expect(results).toHaveLength(1);
  });
});
