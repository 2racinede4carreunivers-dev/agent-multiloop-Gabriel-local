# ===========================================
# Agent IA Local Mathematique - Dockerfile CLI (Fusion Finale)
# ===========================================

FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libportaudio2 \
    portaudio19-dev \
    libasound2-dev \
    libpulse-dev \
    ffmpeg \
    espeak \
    wget \
    unzip \
    libgomp1 \
    libwww-perl \
    libxml2 \
    libxslt1.1 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libglib2.0-0 \
    openjdk-21-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://isabelle.in.tum.de/website-Isabelle2025-2/dist/Isabelle2025-2_linux.tar.gz -O /tmp/isabelle.tar.gz \
    && tar -xzf /tmp/isabelle.tar.gz -C /opt \
    && rm /tmp/isabelle.tar.gz

ENV ISABELLE_HOME=/opt/Isabelle2025-2
ENV PATH="$ISABELLE_HOME/bin:$PATH"

WORKDIR /home/agent/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements-cli.txt .
RUN pip install --no-cache-dir -r requirements-cli.txt

RUN useradd --create-home --shell /bin/bash agent
COPY --chown=agent:agent . .

RUN mkdir -p data logs templates/email && chown -R agent:agent .

USER agent

VOLUME ["/home/agent/app/data", "/home/agent/app/logs"]

CMD ["python", "main_cli.py"]
