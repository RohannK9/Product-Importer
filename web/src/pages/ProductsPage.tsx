import type { FormEvent } from "react";
import { useMemo, useState } from "react";
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import {
  bulkDeleteProducts,
  createProduct,
  deleteProduct,
  fetchProducts,
  updateProduct,
} from "../api/products";
import type {
  Product,
  ProductCreateInput,
  ProductListResponse,
  ProductUpdateInput,
} from "../types";
import { apiErrorMessage } from "../api/client";

type FilterStatus = "all" | "active" | "inactive";

interface ProductModalState {
  open: boolean;
  mode: "create" | "edit";
  product?: Product;
}

const PAGE_SIZE = 10;

export function ProductsPage() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    sku: "",
    query: "",
    status: "all" as FilterStatus,
  });
  const [modal, setModal] = useState<ProductModalState>({
    open: false,
    mode: "create",
  });
  const [confirmationText, setConfirmationText] = useState("");
  const [bulkDeleteMessage, setBulkDeleteMessage] = useState<string | null>(null);

  const productsQuery = useQuery<ProductListResponse>({
    queryKey: ["products", page, filters],
    queryFn: () =>
      fetchProducts({
        page,
        page_size: PAGE_SIZE,
        sku: filters.sku || undefined,
        query: filters.query || undefined,
        is_active:
          filters.status === "all" ? undefined : filters.status === "active",
      }),
    placeholderData: (previousData) => previousData,
  });

  const createMutation = useMutation({
    mutationFn: (payload: ProductCreateInput) => createProduct(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      setModal({ open: false, mode: "create" });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: ProductUpdateInput }) =>
      updateProduct(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      setModal({ open: false, mode: "create" });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: () => bulkDeleteProducts(confirmationText),
    onSuccess: (data) => {
      setBulkDeleteMessage(`${data.deleted_count} products deleted.`);
      setConfirmationText("");
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (error) => setBulkDeleteMessage(apiErrorMessage(error)),
  });

  const totalPages = useMemo(() => {
    if (!productsQuery.data) return 1;
    return Math.max(1, Math.ceil(productsQuery.data.total / PAGE_SIZE));
  }, [productsQuery.data]);

  const openCreateModal = () => setModal({ open: true, mode: "create" });
  const openEditModal = (product: Product) =>
    setModal({ open: true, mode: "edit", product });
  const closeModal = () => setModal({ open: false, mode: "create", product: undefined });

  const handleCreateOrUpdate = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const payload: ProductCreateInput = {
      sku: formData.get("sku")?.toString().trim() || "",
      name: formData.get("name")?.toString().trim() || "",
      description: formData.get("description")?.toString() || undefined,
      price: Number(formData.get("price") || 0),
      currency: formData.get("currency")?.toString().toUpperCase() || "USD",
      is_active: formData.get("is_active") === "true",
    };

    if (!payload.sku || !payload.name) {
      return;
    }

    if (modal.mode === "create") {
      createMutation.mutate(payload);
    } else if (modal.product) {
      const updatePayload: ProductUpdateInput = {
        name: payload.name,
        description: payload.description,
        price: payload.price,
        currency: payload.currency,
        is_active: payload.is_active,
      };
      updateMutation.mutate({ id: modal.product.id, payload: updatePayload });
    }
  };

  const resetFilters = () => {
    setFilters({ sku: "", query: "", status: "all" });
    setPage(1);
  };

  return (
    <div className="stack">
      <section className="app-section">
        <h2 className="section-title">Products</h2>
        <p className="section-description">
          Manage products, update descriptions, and control availability.
        </p>

        <form
          className="form-grid two-columns"
          onSubmit={(event) => {
            event.preventDefault();
            setPage(1);
            queryClient.invalidateQueries({ queryKey: ["products"] });
          }}
        >
          <label className="label">
            SKU
            <input
              className="input"
              value={filters.sku}
              onChange={(e) => setFilters((prev) => ({ ...prev, sku: e.target.value }))}
              placeholder="SKU"
            />
          </label>
          <label className="label">
            Name or Description
            <input
              className="input"
              value={filters.query}
              onChange={(e) => setFilters((prev) => ({ ...prev, query: e.target.value }))}
              placeholder="Search keyword"
            />
          </label>
          <label className="label">
            Status
            <select
              className="select"
              value={filters.status}
              onChange={(e) =>
                setFilters((prev) => ({ ...prev, status: e.target.value as FilterStatus }))
              }
            >
              <option value="all">All</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </label>
          <div className="stack-row">
            <button type="submit" className="button secondary">
              Apply Filters
            </button>
            <button type="button" className="button" onClick={resetFilters}>
              Reset
            </button>
          </div>
        </form>

        <div className="stack-row" style={{ marginTop: "16px" }}>
          <button type="button" className="button" onClick={openCreateModal}>
            New Product
          </button>
          <div className="stack-row">
            <input
              className="input"
              placeholder="Type DELETE ALL to confirm"
              value={confirmationText}
              onChange={(e) => setConfirmationText(e.target.value)}
              style={{ width: "240px" }}
            />
            <button
              type="button"
              className="button danger"
              disabled={confirmationText.toUpperCase() !== "DELETE ALL"}
              onClick={() => bulkDeleteMutation.mutate()}
            >
              Delete All
            </button>
          </div>
        </div>
        {bulkDeleteMessage && (
          <div
            className={`alert ${bulkDeleteMutation.isError ? "error" : "success"}`}
            style={{ marginTop: "12px" }}
          >
            {bulkDeleteMessage}
          </div>
        )}
      </section>

      <section className="app-section">
        {productsQuery.isLoading ? (
          <p>Loading products...</p>
        ) : productsQuery.isError ? (
          <p className="alert error">
            {apiErrorMessage(productsQuery.error ?? new Error("Failed to load products"))}
          </p>
        ) : productsQuery.data && productsQuery.data.items.length > 0 ? (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Name</th>
                  <th>Price</th>
                  <th>Status</th>
                  <th>Updated</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {productsQuery.data.items.map((product: Product) => (
                  <tr key={product.id}>
                    <td>{product.sku}</td>
                    <td>{product.name}</td>
                    <td>
                      {product.price.toFixed(2)} {product.currency}
                    </td>
                    <td>
                      <span className={`badge ${product.is_active ? "" : "inactive"}`}>
                        {product.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td>{new Date(product.updated_at).toLocaleString()}</td>
                    <td className="stack-row">
                      <button
                        type="button"
                        className="button secondary"
                        onClick={() => openEditModal(product)}
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        className="button danger"
                        onClick={() => deleteMutation.mutate(product.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="stack-row" style={{ marginTop: "16px" }}>
              <button
                type="button"
                className="button secondary"
                disabled={page <= 1}
                onClick={() => setPage((prev) => Math.max(1, prev - 1))}
              >
                Previous
              </button>
              <span>
                Page {page} of {totalPages}
              </span>
              <button
                type="button"
                className="button secondary"
                disabled={page >= totalPages}
                onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
              >
                Next
              </button>
            </div>
          </div>
        ) : (
          <p>No products found.</p>
        )}
      </section>

      {modal.open && (
        <div className="app-modal">
          <div className="app-modal__backdrop" onClick={closeModal} />
          <div className="app-modal__content">
            <h3>{modal.mode === "create" ? "Create Product" : "Edit Product"}</h3>
            <form className="stack" onSubmit={handleCreateOrUpdate}>
              <label className="label">
                SKU
                <input
                  className="input"
                  name="sku"
                  defaultValue={modal.product?.sku || ""}
                  disabled={modal.mode === "edit"}
                  required
                />
              </label>
              <label className="label">
                Name
                <input
                  className="input"
                  name="name"
                  defaultValue={modal.product?.name || ""}
                  required
                />
              </label>
              <label className="label">
                Description
                <textarea
                  className="textarea"
                  name="description"
                  rows={3}
                  defaultValue={modal.product?.description || ""}
                />
              </label>
              <label className="label">
                Price
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  className="input"
                  name="price"
                  defaultValue={modal.product?.price ?? 0}
                  required
                />
              </label>
              <label className="label">
                Currency
                <input
                  className="input"
                  name="currency"
                  maxLength={3}
                  defaultValue={modal.product?.currency || "USD"}
                  required
                />
              </label>
              <label className="label">
                Status
                <select
                  className="select"
                  name="is_active"
                  defaultValue={modal.product?.is_active ? "true" : "false"}
                >
                  <option value="true">Active</option>
                  <option value="false">Inactive</option>
                </select>
              </label>

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
