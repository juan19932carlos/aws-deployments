# Called by `sam build` (BuildMethod: makefile). Runs in this directory because
# samconfig.toml sets build_in_source, so the workspace root is reachable.
# Commands run from the root: `uv export` emits workspace paths relative to it.
ROOT := ../..
REQS := $(ARTIFACTS_DIR)/requirements.txt

build-HelloWorldFunction:
	cd $(ROOT) && uv export --package hello-world --frozen --no-dev --no-editable \
		--no-header --quiet -o $(REQS)
	cd $(ROOT) && uv pip install --target $(ARTIFACTS_DIR) \
		--python-version 3.14 --python-platform x86_64-manylinux2014 \
		--no-installer-metadata --no-compile-bytecode -r $(REQS)
	rm $(REQS)
