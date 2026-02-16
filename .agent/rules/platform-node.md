# Node.js Rules

> **Conditional**: Apply only when Node.js is detected (`package.json` with node engine or `node_modules/`). Skip for non-Node projects.

## Runtime & Deps

- Target Node 20.x LTS. npm default; commit `package-lock.json`. Production deps lean; build/test tools in `devDependencies`.

## Security

- `npm audit --production` before builds. Secrets from env vars/secrets managers only. HTTPS for outbound; validate external payloads.

## Testing & Lint

- `npm test` for full suite. `npm run lint` (ESLint + Prettier) in CI; fail on errors. Fast, deterministic tests; gate e2e behind flags.

## Build & Deploy

- Bundle via `npm run build` to `dist/`. Use local `node_modules/.bin`, not global CLIs. Document env vars in playbooks.

## Observability

- Structured logging (Pino or `JSON.stringify`); redact sensitive fields. Handle unhandled rejections; fail fast.

## Language & Patterns

- ES modules in Node 20; `.cjs` only for interop. `async/await` over callbacks. `const`/`let` only.
- Typed/domain errors mapped to HTTP responses; no stack leaks. Validate all external input at boundaries. Injectable time/randomness.

## Structure

- Organize by feature/layer: handlers → services → repositories. Centralized config module; fail fast on missing vars. No raw queries in controllers. Co-locate tests (`*.test.js`).
