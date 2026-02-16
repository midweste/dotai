# CSS Rules

## Style

- 2-space indent, double quotes for attribute values. BEM or documented naming convention. Shallow selectors (≤3 levels, no SCSS nesting).

## Organization

- Modular component files; no runtime `@import` chains. `kebab-case` filenames matching component/block. Centralize custom properties and breakpoints in utility files.

## Compatibility

- Vanilla CSS; preprocessors only if project mandates. Standard properties first; keep browserslist current if autoprefixing. No hand-written vendor prefixes.

## Performance & Accessibility

- Minimize `!important`; use specificity. CSS custom properties for spacing, color, typography, breakpoints, z-index — central tokens file, no hard-coded values.
- WCAG AA contrast. `prefers-reduced-motion` guards on animations.
