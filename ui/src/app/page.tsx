"use client";

import { useState, useEffect } from "react";
import { Upload, FileText, CheckCircle, Clock, AlertCircle } from "lucide-react";
import { api, Job } from "@/lib/api";

export default function Dashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [profile, setProfile] = useState("Profile B: ADA Title II / WCAG 2.1 AA");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    try {
      const result = await api.uploadDocument(file, profile);
      setJobs([result.job, ...jobs]);
      setFile(null);
    } catch (error) {
      console.error("Upload failed", error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">PDF Accessibility Platform</h1>
          <p className="text-gray-600">Enterprise Remediation & Validation Pipeline</p>
        </header>

        <section className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="md:col-span-1 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Upload className="w-5 h-5" /> Ingest Document
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Select PDF</label>
                <input 
                  type="file" 
                  accept=".pdf"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Compliance Profile</label>
                <select 
                  value={profile}
                  onChange={(e) => setProfile(e.target.value)}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                >
                  <option>Profile A: Section 508</option>
                  <option>Profile B: ADA Title II / WCAG 2.1 AA</option>
                  <option>Profile C: PDF/UA</option>
                </select>
              </div>

              <button 
                onClick={handleUpload}
                disabled={!file || isUploading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
              >
                {isUploading ? "Uploading..." : "Start Remediation"}
              </button>
            </div>
          </div>

          <div className="md:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold mb-4">Active Jobs</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-gray-50 text-gray-700 font-medium">
                  <tr>
                    <th className="px-4 py-2 border-b">Job ID</th>
                    <th className="px-4 py-2 border-b">Status</th>
                    <th className="px-4 py-2 border-b">Stage</th>
                    <th className="px-4 py-2 border-b">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {jobs.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-4 py-8 text-center text-gray-500">No recent jobs found.</td>
                    </tr>
                  ) : (
                    jobs.map((job) => (
                      <tr key={job.job_id}>
                        <td className="px-4 py-3 font-mono text-xs">{job.job_id.slice(0, 8)}...</td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                            job.status === "succeeded" ? "bg-green-100 text-green-700" : 
                            job.status === "failed" ? "bg-red-100 text-red-700" : "bg-blue-100 text-blue-700"
                          }`}>
                            {job.status === "succeeded" && <CheckCircle className="w-3 h-3" />}
                            {job.status === "processing" && <Clock className="w-3 h-3 animate-spin" />}
                            {job.status === "failed" && <AlertCircle className="w-3 h-3" />}
                            {job.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-gray-600">{job.current_stage}</td>
                        <td className="px-4 py-3">
                          <a 
                            href={`/review/${job.document_id}`}
                            className="text-blue-600 hover:underline font-medium"
                          >
                            Review
                          </a>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
