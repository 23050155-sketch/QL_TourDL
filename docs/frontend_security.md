
# HTTT16 - Frontend Security Requirements

## 1. Text Rendering

- Render user-provided content as plain text.
- Use standard React JSX text interpolation.
- Do not insert untrusted content directly into HTML.
- Preserve Vietnamese Unicode and valid punctuation.
- Preserve multiline descriptions and review comments.

## 2. Image URL Security

- Validate image URLs before rendering.
- Accept only approved HTTP/HTTPS URLs.
- Reject malformed URLs and unsupported protocols.
- Use fallback images for invalid legacy URLs.
- Review mixed-content restrictions in HTTPS deployments.

## 3. Error Handling

- Display API errors as plain text.
- Do not render API error messages as HTML.
- Do not expose internal exception details.
- Do not display passwords or sensitive tokens.

## 4. Authentication

- Never log passwords or access tokens.
- Handle HTTP 401 and 403 correctly.
- Handle expired and revoked access tokens.
- Review token storage security before implementation.

## 5. HTTP Security

- Configure Content Security Policy for production.
- Review HTTPS and HSTS configuration.
- Review clickjacking protection.
- Maintain correct Content-Type headers.
- Maintain X-Content-Type-Options: nosniff.

## 6. Security Testing

- Verify plain-text rendering of HTML-like strings.
- Verify safe rendering of descriptions and reviews.
- Verify safe image URL handling.
- Verify API error rendering.
- Verify authorization for protected pages.

## Status

Backend text validation: Implemented.
Browser-side security testing: Pending.
Frontend implementation: Pending.
