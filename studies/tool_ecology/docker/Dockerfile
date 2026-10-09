FROM python:3.12.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_PYTHON_DOWNLOADS=never UV_PYTHON=/usr/local/bin/python3 UV_CACHE_DIR=/opt/uv-cache
COPY requirements.txt /seed/requirements.txt
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir uv==0.9.5 -r /seed/requirements.txt ruff==0.16.6 tree-sitter==0.25.2 tree-sitter-python==0.25.0
ENV PATH=/opt/venv/bin:$PATH VIRTUAL_ENV=/opt/venv
RUN uv run --isolated --no-project --with tree-sitter==0.25.2 --with tree-sitter-python==0.25.0 python -c 'import tree_sitter, tree_sitter_python' && uvx --python /usr/local/bin/python3 --with pytest==8.4.1 --with pytest-json-ctrf==0.5.0 --with pyarrow==18.1.0 --with deepdiff==8.6.1 pytest --version
WORKDIR /workspace
