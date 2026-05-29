# Health Check

Use these commands to validate the DEV deployment at `https://petstore-grpc-dev.fly.dev`.

Using `grpcurl` (recommended):

```bash
grpcurl -d '{}' \
  -proto proto/petstore/v1/health.proto \
  petstore-grpc-dev.fly.dev:443 \
  petstore.v1.Health/Check
```

Using `curl` with gRPC framing:

```bash
printf '\x00\x00\x00\x00\x00' | curl --http2 -i -X POST \
  https://petstore-grpc-dev.fly.dev/petstore.v1.Health/Check \
  -H 'content-type: application/grpc' \
  -H 'te: trailers' \
  --data-binary @-
```

`$'\x00...'` is not reliable for this because shells cannot pass NUL bytes as argv literals.
Piping `printf` into `--data-binary @-` sends the required 5-byte gRPC frame correctly.

Expected `grpcurl` response shape:

```json
{
  "status": "SERVING",
  "mode": "prod",
  "details": {
    "version": "0.1.0",
    "build_date": "<timestamp>",
    "git_commit_sha": "<commit-sha>"
  }
}
```

If you pass any fields, grpcurl will return a validation error because `HealthRequest` is empty.
