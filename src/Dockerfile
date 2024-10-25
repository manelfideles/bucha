# Use an AWS-provided base image for Python
FROM public.ecr.aws/lambda/python:3.12

COPY assets/ ${LAMBDA_TASK_ROOT}/assets
COPY bucha/ ${LAMBDA_TASK_ROOT}/bucha
COPY .env ${LAMBDA_TASK_ROOT}

RUN dnf update -y && \
    dnf install -y wget tar gzip unzip bzip2 libX11 procps && \
    dnf clean all

# Install GeckoDriver
RUN wget -q https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz && \
    tar -xzf geckodriver-v0.34.0-linux64.tar.gz -C /usr/local/bin && \
    rm geckodriver-v0.34.0-linux64.tar.gz && \
    chmod +x /usr/local/bin/geckodriver

# Compile deps
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY main.py ${LAMBDA_TASK_ROOT}

CMD [ "main.handler" ]