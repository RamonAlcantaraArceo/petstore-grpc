# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial petstore-grpc service with Python gRPC server
- Health check endpoint implementing gRPC Health Checking Protocol
- Envoy proxy integration for gRPC-Web support
- Docker Compose setup with multi-container architecture
- Build metadata (build date and git commit SHA) exposed via Health endpoint
- Comprehensive documentation with MkDocs
- CI/CD pipeline with GitHub Actions
- Unit and integration test suite with pytest
- gRPC service definitions in Protocol Buffers v3
- Support for in-memory and PostgreSQL storage modes
- Development environment with uv for Python dependency management
