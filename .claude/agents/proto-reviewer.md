# Proto Reviewer Agent

This specialized agent reviews Protocol Buffer (`.proto`) file changes for best practices and
potential issues.

## Capabilities

The proto-reviewer agent checks for:

### 1. Breaking Changes

- Field number changes or reuse
- Field type changes
- Message or service renames
- Removal of fields without deprecation

### 2. Field Numbering

- Field numbers in optimal range (1-15 for frequent fields)
- No gaps or conflicts
- Reserved field numbers for deleted fields

### 3. Naming Conventions

- PascalCase for messages and services
- snake_case for field names
- Consistent naming patterns

### 4. Documentation

- Service and RPC documentation
- Message and field comments
- Usage examples where appropriate

### 5. Backward Compatibility

- Use of `reserved` for deleted fields
- Proper deprecation markers
- Optional fields for new additions

## When to Invoke

Use this agent when:

- Adding or modifying `.proto` files
- Reviewing pull requests with proto changes
- Planning API versioning strategy

## Example Review

Given a proto change:

```proto
message HealthResponse {
  string status = 1;
  string mode = 2;
  Details details = 3;
  string new_field = 4;  // New field added

  message Details {
    string version = 1;
    string build_date = 2;
    string git_commit_sha = 3;
  }
}
```

The agent would check:

- ✓ New field uses next available number (4)
- ✓ Backward compatible (new field is optional by default in proto3)
- ⚠ Consider documenting the purpose of `new_field`
- ⚠ Field number 4 is still in optimal range (1-15)

## Recommendations After Review

1. **Regenerate stubs:** Run `bash scripts/gen_protos.sh`
2. **Update implementations:** Modify servicers to handle new fields
3. **Add tests:** Cover new field behavior
4. **Document:** Update API docs if user-facing

## Proto Best Practices

### Field Numbers

```proto
// Good: Frequent fields in 1-15 range (single-byte encoding)
message User {
  int32 id = 1;
  string name = 2;
  string email = 3;
  // Less frequent fields can use 16+
  string bio = 16;
}
```

### Reserved Fields

```proto
message User {
  reserved 4, 5;  // Never reuse these numbers
  reserved "old_field";  // Never reuse this name

  int32 id = 1;
  string name = 2;
  string email = 3;
  // Fields 4 and 5 are reserved
  string new_field = 6;
}
```

### Deprecation

```proto
message User {
  int32 id = 1;
  string name = 2 [deprecated = true];  // Mark as deprecated
  string full_name = 3;  // Replacement field
}
```

### Documentation

```proto
// User represents a registered user in the system.
message User {
  // Unique identifier for the user (auto-generated).
  int32 id = 1;

  // User's full name (required).
  string name = 2;

  // User's email address (must be valid format).
  string email = 3;
}
```

## Integration with Workflow

This agent should be invoked as part of proto change reviews, ideally before merging to main.
The CI pipeline's proto drift check ensures generated files stay in sync.
