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


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.option("--report-format", "report_format", default="json", type=click.Choice(["json", "earl"]), help="Report format.")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output directory.")
@click.option("--profile", default="profile_b", help="Compliance profile.")
def validate(file_path: Path, report_format: str, output: Path | None, profile: str):
    """Validate a PDF document locally and generate a report."""
    from pdf_accessibility.core.settings import Settings
    from pdf_accessibility.models.compliance import ComplianceProfile
    from pdf_accessibility.services.canonicalize import build_canonical_document
    from pdf_accessibility.services.pdf_parser import parse_pdf
    from pdf_accessibility.services.reporting import EARLReportGenerator
    from pdf_accessibility.services.validation import run_validation_pipeline

    settings = Settings()
    try:
        prof_enum = ComplianceProfile(profile)
    except ValueError:
        prof_enum = ComplianceProfile.profile_b

    click.echo(f"Validating {file_path.name}...")
    
    # 1. Parse
    parser_artifact = parse_pdf(file_path.stem, file_path)
    
    # 2. Canonicalize
    canonical_doc = build_canonical_document(parser_artifact, None)
    
    # 3. Validate
    validation_artifact = run_validation_pipeline(canonical_doc, settings, profile=prof_enum)
    
    # 4. Report
    if report_format == "earl":
        generator = EARLReportGenerator()
        report_content = generator.generate_report(validation_artifact)
        extension = "jsonld"
    else:
        report_content = validation_artifact.model_dump_json(indent=2)
        extension = "json"
        
    if output:
        output.mkdir(parents=True, exist_ok=True)
        report_path = output / f"{file_path.stem}-validation-report.{extension}"
        report_path.write_text(report_content)
        click.echo(f"Validation report saved to {report_path}")
    else:
        click.echo(report_content)


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.option("--report-format", "report_format", default="json", type=click.Choice(["json", "earl"]), help="Report format.")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output directory.")
@click.option("--profile", default="profile_b", help="Compliance profile.")
def process(file_path: Path, report_format: str, output: Path | None, profile: str):
    """Process (remediate and validate) a PDF document locally."""
    from pdf_accessibility.core.settings import Settings
    from pdf_accessibility.models.compliance import ComplianceProfile
    from pdf_accessibility.services.canonicalize import build_canonical_document
    from pdf_accessibility.services.pdf_parser import parse_pdf
    from pdf_accessibility.services.pdf_writer import PdfWriterService
    from pdf_accessibility.services.remediation import run_remediation_pipeline
    from pdf_accessibility.services.reporting import EARLReportGenerator
    from pdf_accessibility.services.validation import run_validation_pipeline

    settings = Settings()
    try:
        prof_enum = ComplianceProfile(profile)
    except ValueError:
        prof_enum = ComplianceProfile.profile_b

    click.echo(f"Processing {file_path.name}...")
    
    # 1. Parse
    parser_artifact = parse_pdf(file_path.stem, file_path)
    
    # 2. Canonicalize
    canonical_doc = build_canonical_document(parser_artifact, None)
    
    # 3. Remediate
    remediated_doc, remediation_artifact = run_remediation_pipeline(canonical_doc, settings, profile=prof_enum)
    
    # 4. Write back
    if output:
        output.mkdir(parents=True, exist_ok=True)
        remediated_pdf_path = output / f"{file_path.stem}-remediated.pdf"
        writer = PdfWriterService(settings)
        writer.write_remediated_pdf(file_path, remediated_pdf_path, remediated_doc)
        click.echo(f"Remediated PDF saved to {remediated_pdf_path}")
    
    # 5. Validate (the remediated document)
    validation_artifact = run_validation_pipeline(remediated_doc, settings, profile=prof_enum)
    
    # 6. Report
    if report_format == "earl":
        generator = EARLReportGenerator()
        report_content = generator.generate_report(validation_artifact)
        extension = "jsonld"
    else:
        report_content = validation_artifact.model_dump_json(indent=2)
        extension = "json"
        
    if output:
        report_path = output / f"{file_path.stem}-validation-report.{extension}"
        report_path.write_text(report_content)
        click.echo(f"Validation report saved to {report_path}")
    else:
        click.echo(report_content)


if __name__ == "__main__":
    cli()
