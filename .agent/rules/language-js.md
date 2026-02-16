# JavaScript Rules (Browser / jQuery)

## Style Guide

- Prefer modern ES modules; use `import`/`export` in browsers that support them, or the project’s bundler if present.
- Enforce semicolons, single quotes, 2-space indentation, trailing commas (ES5), and bracket spacing.
- Keep arrow functions concise but always include parentheses around parameters for readability.
- Use native DOM APIs first; reach for jQuery only when it simplifies cross-browser DOM/event handling already in use by the project.

## Code Organization

- Place shared utilities in dedicated modules; avoid deep relative paths—prefer shallow module hierarchies or documented import maps.
- Co-locate component files (JS + CSS) when it improves clarity, but avoid circular dependencies.
- Name scripts and components using `camelCase` filenames; tests follow `*.test.{js,ts,jsx,tsx}`.
- Avoid Node-specific globals/APIs (`require`, `module`, `process`) in browser code; keep code runtime-agnostic unless explicitly for build tooling.

## Type Safety

- Use JSDoc typedefs (or TypeScript if the project already uses it) for complex structures; provide explicit interfaces for API payloads.
- Validate external data with lightweight runtime guards; avoid shipping server-only validation libs to the client.

## Testing

- Provide `npm test` or `npm run test:js` scripts that cover unit and integration cases; run tests in a browser-like environment (JSDOM/Karma) when DOM or jQuery is involved.
- Favor browser-like test environments; mock platform globals only when required by the framework.
