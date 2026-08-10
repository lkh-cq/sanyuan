import { requestUrl } from "obsidian";

import type {
  HealthResponse,
  RetrieveRequest,
  RetrieveResponse,
  RouterSettings
} from "./types";

function isLoopback(hostname: string): boolean {
  return hostname === "127.0.0.1" || hostname === "localhost" || hostname === "[::1]";
}

function endpointUrl(settings: RouterSettings, path: string): string {
  const endpoint = new URL(settings.endpoint);
  if (endpoint.protocol !== "http:" && endpoint.protocol !== "https:") {
    throw new Error("The sidecar endpoint must use HTTP or HTTPS.");
  }
  if (!isLoopback(endpoint.hostname) && !settings.allowRemoteEndpoint) {
    throw new Error("Remote endpoints require explicit opt-in in settings.");
  }
  const base = endpoint.toString().replace(/\/$/, "");
  return `${base}${path}`;
}

function headers(settings: RouterSettings): Record<string, string> {
  const result: Record<string, string> = { "Content-Type": "application/json" };
  if (settings.authToken.trim()) {
    result.Authorization = `Bearer ${settings.authToken.trim()}`;
  }
  return result;
}

function requireObject(value: unknown): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error("The sidecar returned an invalid JSON object.");
  }
  return value as Record<string, unknown>;
}

export class SanyuanClient {
  constructor(private readonly settings: RouterSettings) {}

  async health(): Promise<HealthResponse> {
    const response = await requestUrl({
      url: endpointUrl(this.settings, "/health"),
      method: "GET",
      headers: headers(this.settings),
      throw: false
    });
    if (response.status < 200 || response.status >= 300) {
      throw new Error(`Sidecar health check failed with HTTP ${response.status}.`);
    }
    const data = requireObject(response.json);
    return {
      status: typeof data.status === "string" ? data.status : "unknown",
      embedding_enabled:
        typeof data.embedding_enabled === "boolean" ? data.embedding_enabled : undefined,
      routing_loaded:
        typeof data.routing_loaded === "boolean" ? data.routing_loaded : undefined
    };
  }

  async retrieve(request: RetrieveRequest): Promise<RetrieveResponse> {
    const response = await requestUrl({
      url: endpointUrl(this.settings, "/v1/retrieve-and-inject"),
      method: "POST",
      headers: headers(this.settings),
      contentType: "application/json",
      body: JSON.stringify(request),
      throw: false
    });
    if (response.status < 200 || response.status >= 300) {
      const data = requireObject(response.json);
      const message = typeof data.error === "string" ? data.error : `HTTP ${response.status}`;
      throw new Error(`Retrieval failed: ${message}`);
    }
    const data = requireObject(response.json);
    if (
      typeof data.query !== "string" ||
      typeof data.triggered !== "boolean" ||
      typeof data.mode !== "string" ||
      typeof data.injection !== "string"
    ) {
      throw new Error("The sidecar retrieval response is incomplete.");
    }
    return {
      query: data.query,
      triggered: data.triggered,
      mode: data.mode as RetrieveResponse["mode"],
      injection: data.injection,
      diagnostics:
        typeof data.diagnostics === "object" && data.diagnostics !== null
          ? (data.diagnostics as Record<string, unknown>)
          : {}
    };
  }
}
