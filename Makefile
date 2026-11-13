.PHONY: test
test:
	uv run tox run-parallel --parallel-no-spinner

.PHONY: build
build:
	uvx --from build pyproject-build --installer uv

.PHONY: deploy
deploy:
	uvx twine upload dist/*
