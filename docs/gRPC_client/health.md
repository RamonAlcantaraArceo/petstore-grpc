# Health Check

Use this command to confirm the server is reachable over gRPC and reflection is enabled.

```bash
grpcurl -plaintext -d '{}' localhost:50051 petstore.v1.Health/Check
```

Expected response:

```json
{
  "status": "SERVING",
  "mode": "dev",
  "details": {
    "version": "0.1.0",
    "build_date": "unknown",
    "git_commit_sha": "unknown"
  }
}
```

If you pass any fields, grpcurl will return a validation error because `HealthRequest` is empty.
