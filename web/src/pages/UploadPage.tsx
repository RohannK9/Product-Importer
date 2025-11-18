import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import {
  QueryClient,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import {
  fetchUploadJob,
  fetchUploadJobs,
  uploadCsv,
} from "../api/uploads";
import type { UploadJob } from "../types";
import { apiErrorMessage } from "../api/client";

interface UploadFormValues {
  file: FileList;
}

const POLL_INTERVAL = 3_000;

const statusLabels: Record<string, string> = {
  received: "Received",
  queued: "Queued",
  parsing: "Parsing",
  validating: "Validating",
  upserting: "Upserting",
  completed: "Completed",
  failed: "Failed",
};

function invalidateUploadJobs(queryClient: QueryClient) {
  queryClient.invalidateQueries({ queryKey: ["upload-jobs"] });
}

export function UploadPage() {
  const queryClient = useQueryClient();
  const [selectedJob, setSelectedJob] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting },
  } = useForm<UploadFormValues>();

  const jobsQuery = useQuery({
    queryKey: ["upload-jobs"],
    queryFn: fetchUploadJobs,
    refetchInterval: POLL_INTERVAL,
  });

  const jobStatusQuery = useQuery({
    queryKey: ["upload-job", selectedJob],
    queryFn: () => fetchUploadJob(selectedJob as string),
    enabled: Boolean(selectedJob),
    refetchInterval: selectedJob ? POLL_INTERVAL : false,
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadCsv(file),
    onSuccess: (data) => {
      setSelectedJob(data.job_id);
      setStatusMessage("Upload started successfully.");
      invalidateUploadJobs(queryClient);
      reset();
    },
    onError: (error) => setStatusMessage(apiErrorMessage(error)),
  });

  useEffect(() => {
    if (jobStatusQuery.data?.status === "completed") {
      setStatusMessage("Upload completed successfully.");
    }
    if (jobStatusQuery.data?.status === "failed") {
      setStatusMessage(jobStatusQuery.data.error || "Upload failed.");
    }
  }, [jobStatusQuery.data]);

  const inProgressJob = useMemo<UploadJob | undefined>(() => {
    if (!selectedJob) return undefined;
    if (jobStatusQuery.data) return jobStatusQuery.data;
    return jobsQuery.data?.find((job) => job.id === selectedJob);
  }, [selectedJob, jobStatusQuery.data, jobsQuery.data]);

  const onSubmit = (values: UploadFormValues) => {
    const [file] = values.file || [];
    if (!file) {
      setStatusMessage("Please choose a CSV file to upload.");
      return;
    }
    if (!file.name.toLowerCase().endsWith(".csv")) {
      setStatusMessage("Only CSV files are supported.");
      return;
    }
    uploadMutation.mutate(file);
  };

  return (
    <div className="stack">
      <section className="app-section">
        <h2 className="section-title">Upload CSV</h2>
        <p className="section-description">
          Upload a CSV up to 500k rows. SKU collisions will be overwritten.
        </p>

        <form className="stack" onSubmit={handleSubmit(onSubmit)}>
          <label className="label">
            CSV file
            <input
              type="file"
              accept=".csv"
              className="input"
              {...register("file")}
              disabled={isSubmitting || uploadMutation.isPending}
            />
          </label>
          <button
            type="submit"
            className="button"
            disabled={isSubmitting || uploadMutation.isPending}
          >
            {uploadMutation.isPending ? "Uploading..." : "Start Upload"}
          </button>
        </form>

        {statusMessage && (
          <div
            className={`alert ${
              jobStatusQuery.data?.status === "failed" ? "error" : "success"
            }`}
          >
            {statusMessage}
          </div>
        )}

        {inProgressJob && (
          <div className="card">
            <h3>Current Job</h3>
            <p>
              <strong>Status:</strong> {statusLabels[inProgressJob.status] || inProgressJob.status}
            </p>
            <p>
              <strong>Processed rows:</strong> {inProgressJob.processed_rows}
              {typeof inProgressJob.total_rows === "number"
                ? ` / ${inProgressJob.total_rows}`
                : ""}
            </p>
            {inProgressJob.error && (
              <p className="alert error">{inProgressJob.error}</p>
            )}
          </div>
        )}
      </section>

      <section className="app-section">
        <h3 className="section-title">Recent Uploads</h3>
        {jobsQuery.isLoading ? (
          <p>Loading jobs...</p>
        ) : jobsQuery.isError ? (
          <p className="alert error">
            {apiErrorMessage((jobsQuery.error as unknown) || new Error("Failed to load"))}
          </p>
        ) : jobsQuery.data && jobsQuery.data.length > 0 ? (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Status</th>
                  <th>Processed</th>
                  <th>Updated</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {jobsQuery.data.map((job) => (
                  <tr key={job.id}>
                    <td>{job.filename}</td>
                    <td>{statusLabels[job.status] || job.status}</td>
                    <td>
                      {job.processed_rows}
                      {typeof job.total_rows === "number" ? ` / ${job.total_rows}` : ""}
                    </td>
                    <td>{new Date(job.updated_at).toLocaleString()}</td>
                    <td>
                      <button
                        type="button"
                        className="button secondary"
                        onClick={() => setSelectedJob(job.id)}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No uploads yet.</p>
        )}
      </section>
    </div>
  );
}
