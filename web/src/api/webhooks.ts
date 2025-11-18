import { apiClient } from "./client";
import type {
  Webhook,
  WebhookCreateInput,
  WebhookDelivery,
  WebhookListResponse,
  WebhookTestResponse,
  WebhookUpdateInput,
} from "../types";

export const fetchWebhooks = async (): Promise<Webhook[]> => {
  const { data } = await apiClient.get<WebhookListResponse>("/webhooks");
  return data.items;
};

export const createWebhook = async (
  payload: WebhookCreateInput
): Promise<Webhook> => {
  const { data } = await apiClient.post<Webhook>("/webhooks", payload);
  return data;
};

export const updateWebhook = async (
  webhookId: string,
  payload: WebhookUpdateInput
): Promise<Webhook> => {
  const { data } = await apiClient.put<Webhook>(`/webhooks/${webhookId}`, payload);
  return data;
};

export const deleteWebhook = async (webhookId: string): Promise<void> => {
  await apiClient.delete(`/webhooks/${webhookId}`);
};

export const testWebhook = async (
  webhookId: string
): Promise<WebhookTestResponse> => {
  const { data } = await apiClient.post<WebhookTestResponse>(
    `/webhooks/${webhookId}/test`
  );
  return data;
};

export const fetchWebhookDeliveries = async (
  webhookId: string
): Promise<WebhookDelivery[]> => {
  const { data } = await apiClient.get<WebhookDelivery[]>(
    `/webhooks/${webhookId}/deliveries`
  );
  return data;
};
