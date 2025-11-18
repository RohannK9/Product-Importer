import { apiClient } from "./client";
import type {
  UploadInitResponse,
  UploadJob,
  UploadJobListResponse,
} from "../types";

export const uploadCsv = async (file: File): Promise<UploadInitResponse> => {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post<UploadInitResponse>("/uploads", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return data;
};

export const fetchUploadJobs = async (): Promise<UploadJob[]> => {
  const { data } = await apiClient.get<UploadJobListResponse>("/uploads");
  return data.items;
};

export const fetchUploadJob = async (jobId: string): Promise<UploadJob> => {
  const { data } = await apiClient.get<UploadJob>(`/uploads/${jobId}`);
  return data;
};
