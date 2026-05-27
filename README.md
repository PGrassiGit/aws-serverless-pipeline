# AWS Serverless Pipeline

## Problem

This project shows an AWS path for SaaS usage events.

It separates raw files, processed files, and failed files, and keeps the Lambda handler testable without AWS credentials.

## Data Flow

S3 raw usage file -> queue or event rule -> Lambda processor -> processed usage file

Invalid records -> failed usage prefix

## Design Choices

- S3 stores raw and processed usage data.
- SQS provides a buffer and DLQ pattern for failed processing.
- Lambda handles lightweight validation and routing.
- IAM is scoped to raw reads, processed writes, failed writes, and logs.
- Terraform is included as a reference and is not required for local tests.

## How To Run

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

Optional Terraform validation:

```bash
make terraform-validate
```

## Tests

The tests cover S3 event parsing, processed and failed key routing, usage event validation, and local processing counts.

## Production Notes

- Failed records should be replayable from the failed prefix.
- Queue depth and Lambda errors should have CloudWatch alarms.
- Bucket names, regions, and IAM permissions must be reviewed before deployment.
- Athena or Glue can be added after the processed file layout is stable.

## Docs

- [Architecture](docs/architecture.md)

## Portuguese

Este projeto mostra um caminho AWS para eventos de uso de um produto SaaS.

Ele separa arquivos raw, processed e failed, mantendo o handler Lambda testavel sem credenciais AWS.
