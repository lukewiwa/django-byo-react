/**
 * React mount helpers built on top of the core parser. React and react-dom
 * are peer dependencies — install them in your app, not transitively here.
 */
import { createElement, type ComponentType } from "react";
import { createRoot, type Root } from "react-dom/client";

import {
  ByoReactError,
  parseProps,
  parsePropsByComponentName,
  parsePropsById,
  type FindOptions,
  type Validator,
} from "./index.js";

export interface MountOptions<T> extends FindOptions {
  validate?: Validator<T>;
}

export interface MountedRoot<T> {
  container: HTMLElement;
  root: Root;
  props: T;
  componentName: string | undefined;
  unmount: () => void;
}

function mountElement<P extends object>(
  container: HTMLElement,
  Component: ComponentType<P>,
  props: P,
  componentName: string | undefined,
): MountedRoot<P> {
  const root = createRoot(container);
  root.render(createElement(Component, props));
  return {
    container,
    root,
    props,
    componentName,
    unmount: () => root.unmount(),
  };
}

/** Mount `Component` into a container you already have a reference to. */
export function mount<P extends object>(
  container: HTMLElement,
  Component: ComponentType<P>,
  options: MountOptions<P> = {},
): MountedRoot<P> {
  const props = parseProps<P>(container, options.validate);
  return mountElement(
    container,
    Component,
    props,
    container.getAttribute("data-component-name") ?? undefined,
  );
}

/** Mount `Component` into the container with the given id. */
export function mountById<P extends object>(
  id: string,
  Component: ComponentType<P>,
  options: MountOptions<P> = {},
): MountedRoot<P> {
  const { container, props, componentName } = parsePropsById<P>(
    id,
    options.validate,
    options,
  );
  return mountElement(container, Component, props, componentName);
}

/**
 * Mount `Component` into every container rendered with
 * `component_name="<name>"`. Returns one `MountedRoot` per element so the
 * caller can unmount individually.
 */
export function mountAllByComponentName<P extends object>(
  name: string,
  Component: ComponentType<P>,
  options: MountOptions<P> = {},
): Array<MountedRoot<P>> {
  return parsePropsByComponentName<P>(name, options.validate, options).map(
    ({ container, props, componentName }) =>
      mountElement(container, Component, props, componentName),
  );
}

export { ByoReactError };
export type { Validator };
