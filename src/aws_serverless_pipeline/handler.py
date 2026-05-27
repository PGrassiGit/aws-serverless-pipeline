from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from urllib.parse import unquote_plus


@dataclass(frozen=True)
class UsageObject:
    bucket: str
    input_key: str
    processed_key: str
    failed_key: str


def processed_key(input_key: str) -> str:
    name = input_key.rsplit("/", maxsplit=1)[-1]
    return f"processed/usage/{name}"


def failed_key(input_key: str) -> str:
    name = input_key.rsplit("/", maxsplit=1)[-1]
    return f"failed/usage/{name}"


def parse_s3_event(event: dict) -> list[UsageObject]:
    objects = []
    for item in event.get("Records", []):
        bucket = item["s3"]["bucket"]["name"]
        key = unquote_plus(item["s3"]["object"]["key"])
        objects.append(
            UsageObject(
                bucket=bucket,
                input_key=key,
                processed_key=processed_key(key),
                failed_key=failed_key(key),
            )
        )
    return objects


def validate_usage_event(record: dict) -> list[str]:
    errors = []
    required_fields = {"event_id", "customer_id", "subscription_id", "event_type", "quantity"}
    missing = required_fields - record.keys()
    if missing:
        errors.append(f"missing fields: {', '.join(sorted(missing))}")
    if "quantity" in record and int(record["quantity"]) < 0:
        errors.append("quantity cannot be negative")
    return errors


def process_usage_lines(lines: list[str]) -> dict[str, int]:
    valid = 0
    invalid = 0
    for line in lines:
        record = json.loads(line)
        if validate_usage_event(record):
            invalid += 1
        else:
            valid += 1
    return {"valid": valid, "invalid": invalid}


def route_usage_record(record: dict, source_key: str) -> str:
    if validate_usage_event(record):
        return failed_key(source_key)
    return processed_key(source_key)


def lambda_handler(event: dict, context: object | None = None) -> dict:
    objects = parse_s3_event(event)
    return {
        "received": len(objects),
        "objects": [asdict(item) for item in objects],
    }
