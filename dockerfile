FROM mcr.microsoft.com/azurelinux/base/python:3.12

# Step 1 - Install dependencies
WORKDIR /app

# Install CA certificates
RUN tdnf install -y ca-certificates && \
    update-ca-trust enable && \
    update-ca-trust extract && \
    tdnf clean all

# Set SSL_CERT_FILE for Python
ENV SSL_CERT_FILE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem

# Step 2 - Copy only requirements.txt
COPY requirements.txt /app

# Step 4 - Install pip dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5 - Copy the rest of the files
COPY . .
ENV PYTHONUNBUFFERED=1

# Expose the application port
EXPOSE 80
WORKDIR /app

# do not change the arguments
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]