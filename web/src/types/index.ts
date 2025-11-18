export type UploadStatus =
  | "received"
  | "queued"
  | "parsing"
  | "validating"
  | "upserting"
  | "completed"
  | "failed";

export interface UploadJob {
  id: string;
  filename: string;
  total_rows: number | null;
  processed_rows: number;
  status: UploadStatus;
  error: string | null;
  created_at: string;
  updated_at: string;
}

export interface UploadJobListResponse {
  items: UploadJob[];
}

export interface UploadInitResponse {
  job_id: string;
  status: UploadStatus;
}

export interface Product {
  id: number;
  sku: string;
  name: string;
  description?: string | null;
  price: number;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProductCreateInput {
  sku: string;
  name: string;
  description?: string;
  price: number;
  currency: string;
  is_active: boolean;
}

export interface ProductUpdateInput {
  name?: string;
  description?: string;
  price?: number;
  currency?: string;
  is_active?: boolean;
}

export interface BulkDeleteResponse {
  deleted_count: number;
}

export interface Webhook {
  id: string;
  name: string;
  target_url: string;
  event: string;
  headers?: Record<string, string> | null;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface WebhookListResponse {
  items: Webhook[];
}

export interface WebhookCreateInput {
  name: string;
  target_url: string;
  event: string;
  headers?: Record<string, string>;
  is_enabled: boolean;
}

export interface WebhookUpdateInput {
  name?: string;
  target_url?: string;
  event?: string;
  headers?: Record<string, string>;
  is_enabled?: boolean;
}

export interface WebhookTestResponse {
  status: string;
  response_code: number | null;
  response_time_ms: number | null;
  response_body: string | null;
}

export interface WebhookDelivery {
  id: string;
  event: string;
  status: string;
  response_code: number | null;
  response_time_ms: number | null;
  created_at: string;
}
