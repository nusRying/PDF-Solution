const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface Job {
  job_id: string;
  document_id: string;
  status: "pending" | "processing" | "succeeded" | "failed";
  current_stage: string;
  compliance_profile: string;
  error?: string;
  summary: any;
}

export interface DocumentRecord {
  document_id: string;
  original_filename: string;
  file_size_bytes: number;
  created_at: string;
}

export const api = {
  async uploadDocument(file: File, profile: string) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("profile", profile);

    const response = await fetch(`${API_BASE_URL}/documents`, {
      method: "POST",
      body: formData,
    });
    return response.json();
  },

  async getJobStatus(jobId: string): Promise<Job> {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
    return response.json();
  },

  async getCanonicalOutput(documentId: string) {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}/canonical-output`);
    return response.json();
  },

  async getValidationOutput(documentId: string) {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}/validation-output`);
    return response.json();
  },

  async applyReviewAction(documentId: string, blockId: string, updates: { role?: string, alt_text?: string, is_artifact?: boolean }) {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}/review/actions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        override: {
          block_id: blockId,
          ...updates
        }
      }),
    });
    return response.json();
  }
};
