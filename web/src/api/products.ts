import { apiClient } from "./client";
import type {
  BulkDeleteResponse,
  Product,
  ProductCreateInput,
  ProductListResponse,
  ProductUpdateInput,
} from "../types";

export interface ProductListParams {
  page?: number;
  page_size?: number;
  sku?: string;
  query?: string;
  is_active?: boolean | null;
}

export const fetchProducts = async (
  params: ProductListParams
): Promise<ProductListResponse> => {
  const { data } = await apiClient.get<ProductListResponse>("/products", {
    params,
  });
  return data;
};

export const createProduct = async (
  payload: ProductCreateInput
): Promise<Product> => {
  const { data } = await apiClient.post<Product>("/products", payload);
  return data;
};

export const updateProduct = async (
  productId: number,
  payload: ProductUpdateInput
): Promise<Product> => {
  const { data } = await apiClient.put<Product>(`/products/${productId}`, payload);
  return data;
};

export const deleteProduct = async (productId: number): Promise<void> => {
  await apiClient.delete(`/products/${productId}`);
};

export const bulkDeleteProducts = async (
  confirmationText: string
): Promise<BulkDeleteResponse> => {
  const { data } = await apiClient.post<BulkDeleteResponse>(
    "/products/bulk-delete",
    {
      confirmation_text: confirmationText,
    }
  );
  return data;
};
