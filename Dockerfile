FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends git rsync util-linux \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/wiki-requirements.txt
RUN pip install --no-cache-dir -r /tmp/wiki-requirements.txt

COPY --chmod=755 compile/container-entrypoint.sh /usr/local/bin/wiki-container
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /Transpara/transpara-ai/repos/wiki
USER 1000:1000
EXPOSE 8787
ENTRYPOINT ["/usr/local/bin/wiki-container"]
CMD ["serve"]
