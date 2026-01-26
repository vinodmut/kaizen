# Good vs Bad Guideline Examples

This reference provides extended examples of well-written vs poorly-written guidelines across various scenarios.

## Environment & Tooling

### Bad
```json
{
  "content": "Fall back to Python PIL when exiftool is not available",
  "trigger": "When exiftool command fails"
}
```

### Good
```json
{
  "content": "Use Python PIL/Pillow for image metadata extraction in sandboxed environments",
  "rationale": "System tools like exiftool may not be available; PIL is always installable via pip",
  "category": "strategy",
  "trigger": "When extracting image metadata in containerized or sandboxed environments"
}
```

**Why it's better:** The good version recommends PIL as the primary approach in sandboxed contexts, rather than treating it as a fallback when something fails.

---

## Package Management

### Bad
```json
{
  "content": "If npm install fails, try yarn instead",
  "trigger": "When npm throws errors"
}
```

### Good
```json
{
  "content": "Use the package manager already configured in the project (check for yarn.lock vs package-lock.json)",
  "rationale": "Mixing package managers causes dependency resolution conflicts",
  "category": "strategy",
  "trigger": "When installing dependencies in an existing project"
}
```

**Why it's better:** Instead of reactive troubleshooting, it gives a proactive strategy for choosing the right tool from the start.

---

## File Operations

### Bad
```json
{
  "content": "Handle FileNotFoundError when the file doesn't exist",
  "trigger": "When file operations throw exceptions"
}
```

### Good
```json
{
  "content": "Validate file paths and permissions before batch processing operations",
  "rationale": "Early validation prevents partial processing failures mid-operation",
  "category": "recovery",
  "trigger": "When processing multiple files in a pipeline"
}
```

**Why it's better:** Focuses on prevention rather than exception handling.

---

## Memory Management

### Bad
```json
{
  "content": "If you run out of memory, process files in smaller batches",
  "trigger": "When MemoryError occurs"
}
```

### Good
```json
{
  "content": "Implement batch processing with context managers for large file operations",
  "rationale": "Prevents memory leaks and ensures proper resource cleanup",
  "category": "optimization",
  "trigger": "When processing files larger than available memory"
}
```

**Why it's better:** Recommends the right approach from the start based on file size, not memory errors.

---

## API Interactions

### Bad
```json
{
  "content": "Retry with exponential backoff when API returns 429",
  "trigger": "When rate limited"
}
```

### Good
```json
{
  "content": "Implement rate limiting with exponential backoff for external API calls",
  "rationale": "Prevents hitting rate limits and gracefully handles temporary failures",
  "category": "strategy",
  "trigger": "When making multiple requests to external APIs"
}
```

**Why it's better:** Treats rate limiting as expected behavior to design for, not an error to handle.

---

## Database Operations

### Bad
```json
{
  "content": "Use transactions to rollback on error",
  "trigger": "When database operations fail"
}
```

### Good
```json
{
  "content": "Wrap related database operations in transactions for atomicity",
  "rationale": "Ensures data consistency and enables clean rollback if any operation fails",
  "category": "strategy",
  "trigger": "When performing multiple related database writes"
}
```

**Why it's better:** Frames transactions as a design pattern, not an error recovery mechanism.

---

## Permission Issues

### Bad
```json
{
  "content": "Request elevated permissions if write fails",
  "trigger": "When permission denied errors occur"
}
```

### Good
```json
{
  "content": "Write outputs to user-writable directories (~/Documents, /tmp, or project-local paths)",
  "rationale": "System directories often require elevated permissions; user directories are always accessible",
  "category": "strategy",
  "trigger": "When generating output files in any environment"
}
```

**Why it's better:** Recommends accessible paths from the start rather than escalating permissions.

---

## Testing

### Bad
```json
{
  "content": "Mock external services when tests fail due to network issues",
  "trigger": "When tests fail intermittently"
}
```

### Good
```json
{
  "content": "Use mocks and fixtures for external service dependencies in tests",
  "rationale": "Ensures deterministic test results and faster execution",
  "category": "strategy",
  "trigger": "When writing tests that involve external APIs or services"
}
```

**Why it's better:** Presents mocking as a best practice, not a workaround for flaky tests.

---

## Summary: Key Principles

1. **Proactive over reactive**: State what to do, not what failed
2. **Context-based triggers**: Use situational context, not error conditions
3. **Include rationale**: Explain why the approach works
4. **Be specific**: Generic advice is less actionable
5. **Design patterns over fixes**: Frame recommendations as best practices
