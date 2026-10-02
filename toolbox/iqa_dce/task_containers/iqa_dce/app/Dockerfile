FROM python:3.10.13-slim

LABEL name="IQA_DCE_tool"
LABEL version="1.1"

# Install C/C++ build tools required to compile pyradiomics extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home

# Pre-upgrade core packaging tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Leverage Docker layer caching: install requirements before copying code
COPY iqa_dce_tool_EUCAIM/requirements.txt ./requirements.txt

# Pre-install numpy & build helpers, then install pyradiomics without isolation
RUN pip install --no-cache-dir numpy==1.26.4 versioneer
RUN pip install --no-cache-dir --no-build-isolation pyradiomics

# Install remaining dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the PyTorch cache directory exists before copying checkpoint weights
RUN mkdir -p /root/.cache/torch/hub/checkpoints

# Fix the casing warning on COPY
COPY brisque_svm_weights.pt /root/.cache/torch/hub/checkpoints/brisque_svm_weights.pt

# Copy project files
COPY iqa_dce_tool_EUCAIM/ ./

# Set Python script as the fixed entrypoint
ENTRYPOINT ["python3", "./IQA_DCE_tool.py"]

# Default arguments (empty list allows passing custom flags like --help, -i, etc.)
CMD []