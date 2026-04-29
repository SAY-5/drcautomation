FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY drcautomation ./drcautomation
RUN pip install --no-cache-dir -e . && \
    useradd -m -u 1001 drc
USER drc
ENTRYPOINT ["drcrun"]
