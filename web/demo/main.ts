import { checkHealth } from "../grpc/HealthClient";

const statusEl = document.getElementById("status")!;
const detailsEl = document.getElementById("details")!;
const button = document.getElementById("check") as HTMLButtonElement;

async function run(): Promise<void> {
  statusEl.textContent = "Checking…";
  detailsEl.textContent = "";
  try {
    const result = await checkHealth();
    console.log("Health response:", result);
    statusEl.textContent = `Status: ${result.status} (mode=${result.mode})`;
    detailsEl.textContent = JSON.stringify(result.details, null, 2);
  } catch (err) {
    console.error(err);
    statusEl.textContent = `Error: ${(err as Error).message}`;
  }
}

button.addEventListener("click", run);
run();
