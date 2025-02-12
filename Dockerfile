# Base image
FROM quay.io/jupyter/scipy-notebook:2024-12-23

# Install system dependencies as root
USER root

# Combine all apt-get operations into a single layer
RUN apt-get update -q && \
    apt-get install -yqq \
    texlive-latex-extra \
    lmodern \
    curl \
    dumb-init \
    git \
    htop \
    nginx \
    make \
    tmux \
    vim \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to notebook user
USER ${NB_UID}

# Set up environment variables
ENV PATH="/home/${NB_USER}/.local/bin:${PATH}"
ENV SHELL="/bin/bash"

# Configure workspace directories
WORKDIR /work/
WORKDIR ${HOME}

# Install Python dependencies
COPY requirements.txt /tmp/
COPY app.py /work/app.py
RUN pip install -U pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy and process post-build scripts
COPY postBuild /tmp/

# Configure Jupyter
COPY jupyter_notebook_config.py /home/${NB_USER}/.jupyter/
USER root
RUN chown ${NB_USER} /home/${NB_USER}/.jupyter/jupyter_notebook_config.py && \
    chmod 644 /home/${NB_USER}/.jupyter/jupyter_notebook_config.py
USER ${NB_USER}

# Run post-build script
RUN sh /tmp/postBuild

# Create startup script
RUN echo "streamlit run /work/app.py --server.address 0.0.0.0 --server.port 8501 --server.enableCORS False --server.enableXsrfProtection False --browser.gatherUsageStats False" > start.sh && \
RUN  chmod +x start.sh

# Use dumb-init as entrypoint
CMD ["dumb-init", "./start.sh"]
