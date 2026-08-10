export type RetrievalMode = "full" | "fast" | "minimal";
export type TriggerPolicy = "always" | "auto" | "never";

export interface RouterSettings {
  endpoint: string;
  topK: number;
  mode: RetrievalMode;
  smartTriggerPolicy: TriggerPolicy;
  authToken: string;
  allowRemoteEndpoint: boolean;
}

export const DEFAULT_SETTINGS: RouterSettings = {
  endpoint: "http://127.0.0.1:8765",
  topK: 8,
  mode: "full",
  smartTriggerPolicy: "auto",
  authToken: "",
  allowRemoteEndpoint: false
};

export interface RetrieveRequest {
  query: string;
  top_k: number;
  mode: RetrievalMode;
  trigger_policy: TriggerPolicy;
  query_axes?: string[];
  current_path?: string;
}

export interface RetrieveResponse {
  query: string;
  triggered: boolean;
  mode: RetrievalMode;
  injection: string;
  diagnostics: Record<string, unknown>;
}

export interface HealthResponse {
  status: string;
  embedding_enabled?: boolean;
  routing_loaded?: boolean;
}
