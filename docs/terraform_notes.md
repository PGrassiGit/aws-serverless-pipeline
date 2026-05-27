# Terraform Notes

## Deployable Pieces

- S3 buckets for raw and processed usage files
- SQS queue and dead-letter queue
- IAM role and policy for Lambda
- CloudWatch log group

## Reference Pieces

The Terraform does not package or deploy the Lambda function. It shows the resource boundaries and permissions that would support the handler.

## Review Points

- The Lambda reads only `raw/usage/*`.
- The Lambda writes only `processed/usage/*` and `failed/usage/*`.
- The queue has a DLQ with `maxReceiveCount` set to 3.
- Bucket names are variables and should be reviewed before deployment.
