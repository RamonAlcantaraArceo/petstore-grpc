# User Service grpcurl Samples

The user service also uses the DB-backed launch profile. Start the server with
`petstore-grpc: debug database`, or run with `STORAGE_MODE=local` and a valid `DATABASE_URL`.

## Create a user

```bash
grpcurl -plaintext -d '{"user":{"username":"jane.doe","email":"jane@example.com","firstName":"Jane","lastName":"Doe"},"password":"secret"}' localhost:50051 petstore.v1.UserService/CreateUser
```

## Create multiple users

```bash
grpcurl -plaintext -d '{"users":[{"user":{"username":"alice","email":"alice@example.com"},"password":"secret"},{"user":{"username":"bob","email":"bob@example.com"},"password":"secret"}]}' localhost:50051 petstore.v1.UserService/CreateUsersWithList
```

## Get a user by name

```bash
grpcurl -plaintext -d '{"username":"jane.doe"}' localhost:50051 petstore.v1.UserService/GetUserByName
```

## Update a user

```bash
grpcurl -plaintext -d '{"username":"jane.doe","user":{"username":"jane.doe","email":"jane+new@example.com"},"password":"new-secret"}' localhost:50051 petstore.v1.UserService/UpdateUser
```

## Delete a user

```bash
grpcurl -plaintext -d '{"username":"jane.doe"}' localhost:50051 petstore.v1.UserService/DeleteUser
```

## Login and logout

```bash
grpcurl -plaintext -d '{"username":"jane.doe","password":"secret"}' localhost:50051 petstore.v1.UserService/LoginUser
grpcurl -plaintext -d '{}' localhost:50051 petstore.v1.UserService/LogoutUser
```

These RPCs are currently stubbed out by the server and return `UNIMPLEMENTED`.