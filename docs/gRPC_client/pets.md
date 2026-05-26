# FindPetsByStatus

Use the memory debug launch profile with `SEED_DATASET=basic` or `mixed_v1` for these examples.

## Find pets by status

```bash
grpcurl -plaintext -d '{}' localhost:50051 petstore.v1.PetService/FindPetsByStatus
```

To filter explicitly:

```bash
grpcurl -plaintext -d '{"status":"PET_STATUS_AVAILABLE"}' localhost:50051 petstore.v1.PetService/FindPetsByStatus
```

## Find pets by tags

```bash
grpcurl -plaintext -d '{"tags":["friendly","trained"]}' localhost:50051 petstore.v1.PetService/FindPetsByTags
```

## Get a pet by ID

```bash
grpcurl -plaintext -d '{"petId":"1"}' localhost:50051 petstore.v1.PetService/GetPetById
```

## Add a pet

```bash
grpcurl -plaintext -d '{"pet":{"name":"Ollie","photoUrls":["https://example.com/ollie.png"],"status":"PET_STATUS_AVAILABLE"}}' localhost:50051 petstore.v1.PetService/AddPet
```

## Update a pet

```bash
grpcurl -plaintext -d '{"pet":{"id":"1","name":"Buddy Prime","photoUrls":["https://example.com/buddy.png"],"status":"PET_STATUS_AVAILABLE"}}' localhost:50051 petstore.v1.PetService/UpdatePet
```

## Update a pet with form fields

```bash
grpcurl -plaintext -d '{"petId":"1","name":"Buddy Updated","status":"available"}' localhost:50051 petstore.v1.PetService/UpdatePetWithForm
```

## Delete a pet

```bash
grpcurl -plaintext -d '{"petId":"1"}' localhost:50051 petstore.v1.PetService/DeletePet
```

## Upload file

`UploadFile` is defined as a client-streaming RPC, but it is currently not implemented by the server.

## Notes

- `petId`, `photoUrls`, and other field names use grpcurl's JSON form of the proto field names.
- For `FindPetsByTags`, use a seeded dataset that includes tags, such as `mixed_v1`.
