// Browser-side wrapper for the petstore.v1.Health gRPC-Web client.
//
// The generated stubs under ./petstore/v1/ are produced by:
//   bash scripts/gen_grpc_web.sh
//
// They are NOT committed; run the script before bundling this file.

import { HealthClient } from "./petstore/v1/HealthServiceClientPb";
import { HealthRequest, HealthResponse } from "./petstore/v1/health_pb";

export interface HealthStatus {
  status: string;
  mode: string;
  details: {
    version: string;
    buildDate: string;
    gitCommitSha: string;
  };
}

// Default to the Envoy gRPC-Web proxy exposed by docker-compose on :8080.
const DEFAULT_ENDPOINT =
  typeof window !== "undefined" && window.location
    ? `${window.location.protocol}//${window.location.hostname}:8080`
    : "http://localhost:8080";

let cachedClient: HealthClient | null = null;

function getClient(endpoint: string = DEFAULT_ENDPOINT): HealthClient {
  if (!cachedClient) {
    cachedClient = new HealthClient(endpoint, null, null);
  }
  return cachedClient;
}

function toPlain(response: HealthResponse): HealthStatus {
  const details = response.getDetails();
  return {
    status: response.getStatus(),
    mode: response.getMode(),
    details: {
      version: details?.getVersion() ?? "",
      buildDate: details?.getBuildDate() ?? "",
      gitCommitSha: details?.getGitCommitSha() ?? "",
    },
  };
}

export async function checkHealth(
  endpoint: string = DEFAULT_ENDPOINT,
): Promise<HealthStatus> {
  const client = getClient(endpoint);
  const request = new HealthRequest();

  return new Promise<HealthStatus>((resolve, reject) => {
    client.check(request, {}, (err, response) => {
      if (err) {
        reject(new Error(`grpc-web Health.Check failed: ${err.code} ${err.message}`));
        return;
      }
      resolve(toPlain(response));
    });
  });
}
