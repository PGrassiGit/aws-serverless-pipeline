from aws_serverless_pipeline.handler import (
    failed_key,
    lambda_handler,
    parse_s3_event,
    process_usage_lines,
    processed_key,
    route_usage_record,
    validate_usage_event,
)


def test_output_keys_keep_file_name() -> None:
    assert processed_key("raw/usage/events.jsonl") == "processed/usage/events.jsonl"
    assert failed_key("raw/usage/events.jsonl") == "failed/usage/events.jsonl"


def test_parse_s3_event_decodes_key() -> None:
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "usage-raw-bucket"},
                    "object": {"key": "raw/usage/events+2026.jsonl"},
                }
            }
        ]
    }

    result = parse_s3_event(event)

    assert result[0].input_key == "raw/usage/events 2026.jsonl"
    assert result[0].processed_key == "processed/usage/events 2026.jsonl"


def test_validate_usage_event_rejects_negative_quantity() -> None:
    errors = validate_usage_event(
        {
            "event_id": "E1",
            "customer_id": "C1",
            "subscription_id": "S1",
            "event_type": "api_call",
            "quantity": -1,
        }
    )

    assert errors == ["quantity cannot be negative"]


def test_validate_usage_event_rejects_missing_fields() -> None:
    errors = validate_usage_event({"event_id": "E1"})

    assert "missing fields" in errors[0]


def test_process_usage_lines_counts_valid_and_invalid() -> None:
    result = process_usage_lines(
        [
            '{"event_id":"E1","customer_id":"C1","subscription_id":"S1","event_type":"api_call","quantity":1}',
            '{"event_id":"E2","customer_id":"C1","subscription_id":"S1","event_type":"api_call","quantity":-1}',
        ]
    )

    assert result == {"valid": 1, "invalid": 1}


def test_route_usage_record_sends_invalid_record_to_failed_prefix() -> None:
    route = route_usage_record({"event_id": "E1"}, "raw/usage/events.jsonl")

    assert route == "failed/usage/events.jsonl"


def test_lambda_handler_returns_received_objects() -> None:
    result = lambda_handler({"Records": []})

    assert result["received"] == 0
