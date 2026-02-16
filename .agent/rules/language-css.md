# CSS Rules

## Style Guide

- Use 2-space indentation and double quotes for attribute values.
- Prefer BEM or another documented naming convention to avoid selector collisions.
- Keep selectors shallow; avoid chaining more than three levels deep and avoid nested rules (no SCSS-style nesting).

## Organization

- Group related components into modular CSS files and include them deliberately (no runtime `@import` chains).
- Store styles in `kebab-case` filenames, matching the component or block name.
- Centralize CSS custom properties (variables) and breakpoints in dedicated utility files.

## Compatibility

- Stay in vanilla CSS; avoid preprocessors (SCSS/LESS) unless the project already mandates them.
- Rely on standard properties and features first; if a build pipeline adds autoprefixing, keep the browsers list up to date. Do not hand-write vendor prefixes.

## Performance & Accessibility

- Minimize !important usage; rely on specificity instead.
- Use CSS custom properties (variables) for spacing, color, typography, breakpoints, and z-index; define them in a central tokens file and reference them everywhere (no hard-coded values in components).
- Ensure contrast ratios meet WCAG AA; document color palettes and semantic tokens.
- Prefer `prefers-reduced-motion` guards for animations; disable heavy effects for reduced-motion users.
