FROM apache/airflow:2.9.3-python3.11

# Run as root to install system packages
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    rsync \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow

# Extra Python packages needed by the DAGs
RUN pip install --no-cache-dir \
    pyarrow>=14.0 \
    pandas>=2.0 \
    sqlalchemy>=2.0 \
    psycopg2-binary>=2.9 \
    requests>=2.31

# Change airflow UID to 1000 to match the host ubuntu user so the container
# can use the ControlMaster SSH socket (requires matching UID via SO_PEERCRED).
# We patch /etc/passwd directly (sed) rather than usermod to avoid the slow
# file-ownership walk over all pip-installed packages.
USER root
RUN sed -i 's/^airflow:x:50000:/airflow:x:1000:/' /etc/passwd && \
    grep airflow /etc/passwd

USER airflow
