# Architecture

## Problem

Usage events need a cloud path that separates raw files, processed files, and failed files.

## Data Flow

S3 raw zone -> event notification -> Lambda processor -> processed zone

Invalid records -> failed zone

## Design Choices

- S3 keeps raw usage files before processing.
- Lambda handles event parsing and small validation work.
- A queue or EventBridge rule can buffer events before Lambda.
- Failed records should be written to a separate prefix for replay.
- IAM should only allow the Lambda to read raw objects and write processed or failed objects.

## Cost Notes

The design is event-driven. For small billing usage files, this avoids running a server all day.

## Tradeoffs

- The local handler does not call AWS services.
- Terraform shows the resource shape, but deployment is optional.
