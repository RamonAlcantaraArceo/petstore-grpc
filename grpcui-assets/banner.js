(function () {
  "use strict";

  function normalizeEnv(value) {
    if (!value) {
      return "";
    }
    var normalized = String(value).trim().toLowerCase();
    if (["local", "dev", "staging", "prod"].indexOf(normalized) >= 0) {
      return normalized;
    }
    return "";
  }

  function detectEnvironment(hostname) {
    var host = (hostname || "").toLowerCase();

    if (host === "localhost" || host === "127.0.0.1") {
      return "local";
    }
    if (host.indexOf(".petstore-grpc-dev.") !== -1) {
      return "dev";
    }
    if (host.indexOf(".petstore-grpc-staging.") !== -1) {
      return "staging";
    }
    if (host.indexOf(".petstore-grpc.") !== -1) {
      return "prod";
    }
    return "local";
  }

  function resolveEnvironment() {
    var override = normalizeEnv(window.__PETSTORE_GRPCUI_ENV_OVERRIDE__);
    if (override) {
      return override;
    }
    return detectEnvironment(window.location.hostname);
  }

  function insertBanner() {
    if (document.getElementById("petstore-grpcui-banner")) {
      return;
    }

    var env = resolveEnvironment();
    var host = window.location.host;
    var banner = document.createElement("div");
    banner.id = "petstore-grpcui-banner";
    banner.className = "petstore-grpcui-banner petstore-grpcui-banner--" + env;
    banner.textContent = "Connected to: " + env + " — " + host;

    var target = document.body || document.documentElement;
    if (target.firstChild) {
      target.insertBefore(banner, target.firstChild);
      return;
    }
    target.appendChild(banner);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", insertBanner);
    return;
  }
  insertBanner();
})();
