# WordPress Rules

> **Conditional**: Apply only when WordPress is detected (`wp-config.php`, `functions.php`, or `wp-content/`). Skip for non-WordPress projects.

## Security

- `current_user_can()` before privileged actions. Nonces on every state-changing request (forms, REST, AJAX).
- Sanitize input immediately (`sanitize_text_field()`, `sanitize_email()`, etc.). Escape output at render (`esc_html()`, `esc_attr()`, `esc_url()`, `wp_kses()`).
- `$wpdb->prepare()` or `WP_Query` for DB access. `wp_safe_redirect()` over raw headers.
- REST: strict `permission_callback` (never `__return_true`); validate params. AJAX: capability + nonce in both auth/nopriv handlers.

## Organization

- Standard plugin structure with autoloading. Separate admin/public. Domain logic in services; thin admin controllers.
- Project-specific prefix/namespace; avoid globals.

## Performance

- Use WordPress caching/transients. Minimize queries. Optimize asset loading.

## Assets & Frontend

- `wp_enqueue_*` with dependency lists; never hardcode tags. Version with mtime or build hash.
- `wp_localize_script`/`wp_add_inline_script` with sanitized values; prefer REST for dynamic data.
- Block assets via `block.json`, not `functions.php`.

## i18n

- Add translations only when requested. Use `__`, `_e`, `_x`, `esc_html__` with correct text domain. Use `sprintf` placeholders, not concatenation.

## Data & Settings

- `register_setting` with `sanitize_callback`. Flush rewrites only on activation/deactivation.

## Testing

- `WP_UnitTestCase`/integration harnesses. Reset globals/options/hooks between tests. Plugins reuse the central testing harness (`/tests`), not their own bootstrap.
