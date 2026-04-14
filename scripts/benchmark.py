from __future__ import annotations

import time
from pathlib import Path

import requests
from tabulate import tabulate

def run_benchmark(api_url: str, pdf_path: Path, iterations: int = 5):
    print(f"Starting benchmark for {pdf_path.name} ({iterations} iterations)...")
    
    results = []
    total_pages = 0
    
    for i in range(iterations):
        start_time = time.perf_counter()
        
        # Submit
        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path.name, f, "application/pdf")}
            response = requests.post(f"{api_url}/api/v1/documents", files=files)
        
        if response.status_code != 202:
            print(f"Iteration {i+1} failed: {response.text}")
            continue
            
        payload = response.json()
        job_id = payload["job"]["job_id"]
        
        # Poll
        status = "pending"
        while status not in {"succeeded", "failed"}:
            time.sleep(0.5)
            job_response = requests.get(f"{api_url}/api/v1/jobs/{job_id}")
            job_data = job_response.json()
            status = job_data["status"]
            
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        if status == "succeeded":
            pages = job_data["summary"]["page_count"]
            total_pages += pages
            pages_per_sec = pages / duration
            results.append({
                "iteration": i + 1,
                "duration": round(duration, 2),
                "pages": pages,
                "pages_per_sec": round(pages_per_sec, 2)
            })
            print(f"Iteration {i+1}: {pages} pages in {duration:.2f}s ({pages_per_sec:.2f} p/s)")
        else:
            print(f"Iteration {i+1} failed during processing.")

    if results:
        avg_p_s = sum(r["pages_per_sec"] for r in results) / len(results)
        print("\nBenchmark Summary:")
        print(tabulate(results, headers="keys"))
        print(f"\nAverage Throughput: {avg_p_s:.2f} pages/second")
        if avg_p_s >= 30:
            print("SUCCESS: Meets target of >= 30 p/sec")
        else:
            print("WARNING: Below target of 30 p/sec")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--iters", type=int, default=3)
    args = parser.parse_args()
    
    run_benchmark(args.api_url, args.pdf, args.iters)
