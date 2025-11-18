import { useMemo, useState } from "react";
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import {
  createWebhook,
  deleteWebhook,
  fetchWebhookDeliveries,
  fetchWebhooks,
  testWebhook,
  updateWebhook,
} from "../api/webhooks";
import type {
  Webhook,
  WebhookCreateInput,
  WebhookDelivery,
  WebhookTestResponse,
  WebhookUpdateInput,
} from "../types";
import { apiErrorMessage } from "../api/client";

interface WebhookModalState {
  open: boolean;
  mode: "create" | "edit";
  webhook?: Webhook;
}

type FormError = string | null;

export function WebhooksPage() {
  const queryClient = useQueryClient();
  const [modal, setModal] = useState<WebhookModalState>({ open: false, mode: "create" });
  const [selectedWebhook, setSelectedWebhook] = useState<Webhook | null>(null);
  const [testResult, setTestResult] = useState<WebhookTestResponse | null>(null);
  const [formError, setFormError] = useState<FormError>(null);

  const webhooksQuery = useQuery<Webhook[]>({
    queryKey: ["webhooks"],
    queryFn: fetchWebhooks,
  });

  const deliveriesQuery = useQuery<WebhookDelivery[]>({
    queryKey: ["webhook-deliveries", selectedWebhook?.id],
    queryFn: () => fetchWebhookDeliveries(selectedWebhook!.id),
    enabled: Boolean(selectedWebhook),
  });

  const createMutation = useMutation({
    mutationFn: (payload: WebhookCreateInput) => createWebhook(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["webhooks"] });
      setModal({ open: false, mode: "create" });
      setFormError(null);
    },
    onError: (error) => setFormError(apiErrorMessage(error)),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: WebhookUpdateInput }) =>
      updateWebhook(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["webhooks"] });
      setModal({ open: false, mode: "create" });
      setFormError(null);
    },
    onError: (error) => setFormError(apiErrorMessage(error)),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteWebhook(id),
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ["webhooks"] });
      if (selectedWebhook?.id === id) {
        setSelectedWebhook(null);
      }
    },
  });

  const testMutation = useMutation({
    mutationFn: (id: string) => testWebhook(id),
    onSuccess: (data) => setTestResult(data),
    onError: (error) =>
      setTestResult({
        status: "failed",
        response_code: null,
        response_time_ms: null,
        response_body: apiErrorMessage(error),
      }),
  });

  const deliveries = useMemo(() => deliveriesQuery.data ?? [], [deliveriesQuery.data]);

  const openCreateModal = () => {
    setModal({ open: true, mode: "create", webhook: undefined });
    setFormError(null);
  };

  const openEditModal = (webhook: Webhook) => {
    setModal({ open: true, mode: "edit", webhook });
    setFormError(null);
  };

  const closeModal = () => {
    setModal({ open: false, mode: "create", webhook: undefined });
    setFormError(null);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const headersRaw = formData.get("headers")?.toString().trim();
    let headers: Record<string, string> | undefined;

    if (headersRaw) {
      try {
        const parsed = JSON.parse(headersRaw);
        if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
          headers = Object.entries(parsed).reduce<Record<string, string>>(
            (acc, [key, value]) => {
              acc[key] = String(value);
              return acc;
            },
            {}
          );
        } else {
          throw new Error("Headers must be a JSON object");
        }
      } catch (error) {
        setFormError(
          error instanceof Error ? error.message : "Headers must be valid JSON"
        );
        return;
      }
    }

    const payload: WebhookCreateInput = {
      name: formData.get("name")?.toString().trim() || "",
      target_url: formData.get("target_url")?.toString().trim() || "",
      event: formData.get("event")?.toString().trim() || "",
      headers,
      is_enabled: formData.get("is_enabled") === "true",
    };

    if (!payload.name || !payload.target_url || !payload.event) {
      setFormError("Name, target URL, and event are required.");
      return;
    }

    if (modal.mode === "create") {
      createMutation.mutate(payload);
    } else if (modal.webhook) {
      const updatePayload: WebhookUpdateInput = {
        name: payload.name,
        target_url: payload.target_url,
        event: payload.event,
        headers: payload.headers,
        is_enabled: payload.is_enabled,
      };
      updateMutation.mutate({ id: modal.webhook.id, payload: updatePayload });
    }
  };

  return (
    <div className="stack">
      <section className="app-section">
        <h2 className="section-title">Webhooks</h2>
        <p className="section-description">
          Configure webhook endpoints to receive product lifecycle events.
        </p>
        <div className="stack-row">
          <button type="button" className="button" onClick={openCreateModal}>
            New Webhook
          </button>
        </div>
      </section>

      <section className="app-section">
        {webhooksQuery.isLoading ? (
          <p>Loading webhooks...</p>
        ) : webhooksQuery.isError ? (
          <p className="alert error">
            {apiErrorMessage(webhooksQuery.error ?? new Error("Failed to load webhooks"))}
          </p>
        ) : webhooksQuery.data && webhooksQuery.data.length > 0 ? (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Event</th>
                  <th>Status</th>
                  <th>Target URL</th>
                  <th>Updated</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {webhooksQuery.data.map((hook) => (
                  <tr key={hook.id}>
                    <td>{hook.name}</td>
                    <td>{hook.event}</td>
                    <td>
                      <span className={`badge ${hook.is_enabled ? "" : "inactive"}`}>
                        {hook.is_enabled ? "Enabled" : "Disabled"}
                      </span>
                    </td>
                    <td>{hook.target_url}</td>
                    <td>{new Date(hook.updated_at).toLocaleString()}</td>
                    <td className="stack-row">
                      <button
                        type="button"
                        className="button secondary"
                        onClick={() => setSelectedWebhook(hook)}
                      >
                        Deliveries
                      </button>
                      <button
                        type="button"
                        className="button secondary"
                        onClick={() => openEditModal(hook)}
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        className="button"
                        onClick={() => testMutation.mutate(hook.id)}
                      >
                        Test
                      </button>
                      <button
                        type="button"
                        className="button danger"
                        onClick={() => {
                          if (window.confirm("Delete this webhook?")) {
                            deleteMutation.mutate(hook.id);
                          }
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No webhooks configured.</p>
        )}
      </section>

      {selectedWebhook && (
        <section className="app-section">
          <div className="stack-row" style={{ justifyContent: "space-between" }}>
            <h3 className="section-title">Recent Deliveries</h3>
            <button
              type="button"
              className="button secondary"
              onClick={() => deliveriesQuery.refetch()}
            >
              Refresh
            </button>
          </div>
          <p className="section-description">Webhook: {selectedWebhook.name}</p>
          {deliveriesQuery.isLoading ? (
            <p>Loading deliveries...</p>
          ) : deliveriesQuery.isError ? (
            <p className="alert error">
              {apiErrorMessage(
                deliveriesQuery.error ?? new Error("Failed to load deliveries")
              )}
            </p>
          ) : deliveries.length > 0 ? (
            <div className="table-wrapper">
              <table className="table">
                <thead>
                  <tr>
                    <th>Event</th>
                    <th>Status</th>
                    <th>Response</th>
                    <th>Latency (ms)</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {deliveries.map((delivery) => (
                    <tr key={delivery.id}>
                      <td>{delivery.event}</td>
                      <td>{delivery.status}</td>
                      <td>{delivery.response_code ?? "—"}</td>
                      <td>{delivery.response_time_ms ?? "—"}</td>
                      <td>{new Date(delivery.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No deliveries yet.</p>
          )}
        </section>
      )}

      {testResult && (
        <section className="app-section">
          <h3 className="section-title">Test Result</h3>
          <div className={`alert ${testResult.status === "ok" ? "success" : "error"}`}>
            <p>Status: {testResult.status}</p>
            <p>Response code: {testResult.response_code ?? "—"}</p>
            <p>Response time: {testResult.response_time_ms ?? "—"} ms</p>
            {testResult.response_body && <pre>{testResult.response_body}</pre>}
          </div>
        </section>
      )}

      {modal.open && (
        <div className="app-modal">
          <div className="app-modal__backdrop" onClick={closeModal} />
          <div className="app-modal__content">
            <h3>{modal.mode === "create" ? "Create Webhook" : "Edit Webhook"}</h3>
            <form className="stack" onSubmit={handleSubmit}>
              <label className="label">
                Name
                <input
                  className="input"
                  name="name"
                  defaultValue={modal.webhook?.name || ""}
                  required
                />
              </label>
              <label className="label">
                Target URL
                <input
                  className="input"
                  name="target_url"
                  type="url"
                  defaultValue={modal.webhook?.target_url || ""}
                  required
                />
              </label>
              <label className="label">
                Event
                <input
                  className="input"
                  name="event"
                  defaultValue={modal.webhook?.event || "product.created"}
                  required
                />
              </label>
              <label className="label">
                Headers (JSON object)
                <textarea
                  className="textarea"
                  name="headers"
                  rows={3}
                  defaultValue={modal.webhook?.headers ? JSON.stringify(modal.webhook.headers, null, 2) : ""}
                />
              </label>
              <label className="label">
                Status
                <select
                  className="select"
                  name="is_enabled"
                  defaultValue={modal.webhook?.is_enabled ? "true" : "false"}
                >
                  <option value="true">Enabled</option>
                  <option value="false">Disabled</option>
                </select>
              </label>

              {formError && <div className="alert error">{formError}</div>}

              <div className="stack-row" style={{ justifyContent: "flex-end" }}>
                <button type="button" className="button secondary" onClick={closeModal}>
                  Cancel
                </button>
                <button type="submit" className="button">
                  {modal.mode === "create" ? "Create" : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
