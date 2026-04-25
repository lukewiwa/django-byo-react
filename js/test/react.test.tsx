import { afterEach, describe, expect, it } from "vitest";
import { act } from "react";
import type { FC } from "react";

import {
  mount,
  mountAllByComponentName,
  mountById,
} from "../src/react.js";

afterEach(() => {
  document.body.innerHTML = "";
});

interface GreetingProps {
  name: string;
  excited?: boolean;
}

const Greeting: FC<GreetingProps> = ({ name, excited }) => (
  <span data-testid="greeting">
    Hello {name}
    {excited ? "!" : "."}
  </span>
);

function renderTag({
  id,
  scriptId,
  json,
  componentName,
}: {
  id: string;
  scriptId: string;
  json: string;
  componentName?: string;
}): HTMLElement {
  document.body.insertAdjacentHTML(
    "beforeend",
    `<script id="${scriptId}" type="application/json">${json}</script>` +
      `<div id="${id}" data-script-id="${scriptId}"` +
      (componentName ? ` data-component-name="${componentName}"` : "") +
      `></div>`,
  );
  return document.getElementById(id) as HTMLElement;
}

// jsdom needs IS_REACT_ACT_ENVIRONMENT for React's act() to flush effects.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
(globalThis as any).IS_REACT_ACT_ENVIRONMENT = true;

describe("mount", () => {
  it("renders a component with parsed props", async () => {
    const container = renderTag({
      id: "g1",
      scriptId: "g1-data",
      json: '{"name": "Ada", "excited": true}',
    });

    let handle!: ReturnType<typeof mount<GreetingProps>>;
    await act(async () => {
      handle = mount(container, Greeting);
    });

    expect(container.textContent).toBe("Hello Ada!");
    expect(handle.props).toEqual({ name: "Ada", excited: true });
    await act(async () => handle.unmount());
  });

  it("validates props before passing them to the component", async () => {
    renderTag({
      id: "g2",
      scriptId: "g2-data",
      json: '{"name": "Grace"}',
    });

    const validate = (raw: unknown): GreetingProps => {
      const v = raw as GreetingProps;
      if (typeof v?.name !== "string") throw new Error("bad");
      return v;
    };

    let handle!: ReturnType<typeof mountById<GreetingProps>>;
    await act(async () => {
      handle = mountById("g2", Greeting, { validate });
    });

    expect(handle.props.name).toBe("Grace");
    await act(async () => handle.unmount());
  });
});

describe("mountAllByComponentName", () => {
  it("mounts the component into every matching container", async () => {
    renderTag({
      id: "x1",
      scriptId: "x1-data",
      json: '{"name": "One"}',
      componentName: "Greeting",
    });
    renderTag({
      id: "x2",
      scriptId: "x2-data",
      json: '{"name": "Two"}',
      componentName: "Greeting",
    });

    let handles!: ReturnType<typeof mountAllByComponentName<GreetingProps>>;
    await act(async () => {
      handles = mountAllByComponentName("Greeting", Greeting);
    });

    expect(handles).toHaveLength(2);
    expect(document.getElementById("x1")!.textContent).toBe("Hello One.");
    expect(document.getElementById("x2")!.textContent).toBe("Hello Two.");
    expect(handles[0]!.componentName).toBe("Greeting");

    await act(async () => handles.forEach((h) => h.unmount()));
  });
});
