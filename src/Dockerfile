# Use an AWS-provided base image for Python
FROM public.ecr.aws/lambda/python:3.9

COPY assets/ ${LAMBDA_TASK_ROOT}/assets
COPY bucha/ ${LAMBDA_TASK_ROOT}/bucha
COPY .env ${LAMBDA_TASK_ROOT}

# Compile deps
RUN pip freeze > requirements.txt

COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD [ "bucha.main.handler" ]