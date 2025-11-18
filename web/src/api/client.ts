import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL,
  withCredentials: false,
});

export const apiErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    return (
      (error.response?.data as { detail?: string })?.detail ||
      error.message ||
      "Unexpected server error"
    );
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Unexpected error";
};
