# gRPCUrl examples

Making use of vscode-grpc-client extension, you can test your gRPC server with the following
commands:

## Health correct

```shell
grpcurl -plaintext -d '{}' localhost:50051 petstore.v1.Health/Check
```

Expected response:

```json
// Response:

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

## Health bad request

```shell
grpcurl -plaintext -d '{"body": "foo"}' localhost:50051 petstore.v1.Health/Check
```

The expected response is an error message available in the output tab of vscode-grpc-client
extension.
