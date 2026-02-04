# Contributing to Isagawa QA

This is an MVP. Contributions welcome and encouraged.

We're a small team, so reviews may take time. We appreciate your patience.

---

## Ways to Contribute

- **Bug fixes** - Found something broken? Fix it
- **Improvements** - Better code, better docs
- **Port to other frameworks** - Cypress, Playwright, WebdriverIO
- **Port to other languages** - Java, TypeScript, C#
- **Add API testing layer** - REST, GraphQL
- **Add examples** - Common UI patterns, edge cases

---

## How to Contribute

1. Fork the repo
2. Create a branch (`feature/your-feature`)
3. Make your changes
4. Submit a Pull Request

That's it. We'll review when we can.

---

## Porting Guide

### To Other Frameworks

Want to port to Cypress, Playwright, or WebdriverIO? The 5-layer architecture applies:

```
Test → Role → Task → Page → [Your Framework]
```

Replace `WebInterface` (Selenium wrapper) with your framework's equivalent.

### To Other Languages

Want to port to Java, TypeScript, or C#? Same architecture:

- Keep the 5-layer pattern
- Keep the separation of concerns
- Adapt to your language's conventions

### To API Testing

Want to add API testing support? Same 5-layer pattern:

**UI Testing (current):**
```
Test → Role → Task → Page → WebInterface (Selenium)
```

**API Testing:**
```
Test → Role → Task → Endpoint → APIClient (requests/axios)
```

| UI Layer | API Equivalent |
|----------|----------------|
| Page | Endpoint (API resource) |
| WebInterface | APIClient (HTTP wrapper) |

Replace UI interactions with API calls. Same architecture, different interface layer.

---

Start with `framework/_reference/` as your guide.
