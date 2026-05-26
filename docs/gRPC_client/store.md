# Store Service grpcurl Samples

The store service uses the DB-backed launch profile. Start the server with the VS Code
configuration named `petstore-grpc: debug database`, or set `STORAGE_MODE=local` and a valid
`DATABASE_URL` before running `uv run python -m petstore_grpc`.

## Get inventory

```bash
grpcurl -plaintext -d '{}' localhost:50051 petstore.v1.StoreService/GetInventory
```

## Place an order

```bash
grpcurl -plaintext -d '{"order":{"petId":"1","quantity":1,"status":"ORDER_STATUS_PLACED","complete":false}}' localhost:50051 petstore.v1.StoreService/PlaceOrder
```

## Get an order by ID

```bash
grpcurl -plaintext -d '{"orderId":"1"}' localhost:50051 petstore.v1.StoreService/GetOrderById
```

## Delete an order

```bash
grpcurl -plaintext -d '{"orderId":"1"}' localhost:50051 petstore.v1.StoreService/DeleteOrder
```