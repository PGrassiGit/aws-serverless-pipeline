terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "usage_raw" {
  bucket = var.raw_bucket_name
}

resource "aws_s3_bucket" "usage_processed" {
  bucket = var.processed_bucket_name
}

resource "aws_sqs_queue" "usage_dlq" {
  name                      = "portfolio-usage-events-dlq"
  message_retention_seconds = 1209600
}

resource "aws_sqs_queue" "usage_events" {
  name                       = "portfolio-usage-events"
  visibility_timeout_seconds = 60

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.usage_dlq.arn
    maxReceiveCount     = 3
  })
}

resource "aws_iam_role" "lambda_role" {
  name = "portfolio-usage-processor-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name = "portfolio-usage-processor-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.usage_raw.arn}/raw/usage/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = [
          "${aws_s3_bucket.usage_processed.arn}/processed/usage/*",
          "${aws_s3_bucket.usage_processed.arn}/failed/usage/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.lambda_logs.arn}:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/portfolio-usage-processor"
  retention_in_days = 14
}
