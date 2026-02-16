# JavaScript Rules (Browser / jQuery)

## Style

- ES modules (`import`/`export`) or project bundler. Semicolons, single quotes, 2-space indent, trailing commas (ES5), bracket spacing.
- Parentheses on arrow params. Native DOM APIs first; jQuery only when already in use by project.

## Organization

- Shared utilities in dedicated modules; shallow hierarchies. Co-locate JS + CSS per component.
- `camelCase` filenames; tests as `*.test.{js,ts,jsx,tsx}`. No Node globals (`require`, `process`) in browser code.

## Type Safety

- JSDoc typedefs (or TypeScript if project uses it) for complex structures. Lightweight runtime guards for external data.

## Testing

- `npm test` / `npm run test:js` covering unit + integration. Browser-like env (JSDOM/Karma) for DOM/jQuery. Mock platform globals only when framework requires.
