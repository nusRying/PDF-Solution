from __future__ import annotations

from pathlib import Path

import click
import requests
from tabulate import tabulate

from pdf_accessibility.core.settings import get_settings


@click.group()
def cli():
    """PDF Accessibility Remediation Platform CLI."""
    pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.option("--profile", default="Profile B: ADA Title II / WCAG 2.1 AA", help="Compliance profile to use.")
@click.option("--api-url", default="http://127.0.0.1:8000", help="API base URL.")
def submit(file_path: Path, profile: str, api_url: str):
    """Submit a PDF for remediation."""
    click.echo(f"Submitting {file_path.name} with profile: {profile}...")
    
    url = f"{api_url}/api/v1/documents"
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, "application/pdf")}
        data = {"profile": profile}
        response = requests.post(url, files=files, data=data)
    
    if response.status_code == 202:
        payload = response.json()
        job_id = payload["job"]["job_id"]
        click.echo(f"Job submitted successfully. Job ID: {job_id}")
    else:
        click.echo(f"Failed to submit job: {response.text}", err=True)


@cli.command()
@click.argument("job_id")
@click.option("--api-url", default="http://127.0.0.1:8000", help="API base URL.")
def status(job_id: str, api_url: str):
    """Check the status of a remediation job."""
    url = f"{api_url}/api/v1/jobs/{job_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        job = response.json()
        click.echo(f"Job ID: {job['job_id']}")
        click.echo(f"Status: {job['status']}")
        click.echo(f"Stage: {job['current_stage']}")
        if job.get("error"):
            click.echo(f"Error: {job['error']}", fg="red")
    else:
        click.echo(f"Failed to fetch job status: {response.text}", err=True)


@cli.command()
@click.argument("document_id")
@click.option("--format", "report_format", default="json", type=click.Choice(["json", "earl"]), help="Report format.")
@click.option("--api-url", default="http://127.0.0.1:8000", help="API base URL.")
def report(document_id: str, report_format: str, api_url: str):
    """Fetch the validation report for a document."""
    url = f"{api_url}/api/v1/documents/{document_id}/validation-output"
    response = requests.get(url)
    
    if response.status_code == 200:
        artifact = response.json()
        if report_format == "earl":
            # In a real scenario, the API might handle this conversion
            # For now, we'll demonstrate client-side conversion or a separate endpoint
            click.echo("Generating EARL report locally...")
            from pdf_accessibility.models.validation import ValidationArtifact
            from pdf_accessibility.services.reporting import EARLReportGenerator
            
            val_artifact = ValidationArtifact.model_validate(artifact)
            generator = EARLReportGenerator()
            earl_json = generator.generate_report(val_artifact)
            click.echo(earl_json)
        else:
            import json
            click.echo(json.dumps(artifact, indent=2))
    else:
        click.echo(f"Failed to fetch report: {response.text}", err=True)


if __name__ == "__main__":
    cli()
