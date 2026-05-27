.PHONY: test terraform-validate

test:
	python -m pytest

terraform-validate:
	cd infra && terraform init -backend=false && terraform validate
