FROM python:3.11.3

WORKDIR /app

COPY ./requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY ./main.py .
COPY cas_api ./customer_analysis_service
COPY cas_worker/db/models ./customer_analysis_service/db
COPY cas_worker/db/repository ./customer_analysis_service/db
COPY cas_worker/db/database.py ./customer_analysis_service/db
COPY cas_worker/db/__init__.py ./customer_analysis_service/db
COPY cas_worker/tasks/analysis ./customer_analysis_service/services
COPY cas_worker/tasks/__init__.py ./customer_analysis_service/services
COPY config.py ./customer_analysis_service
COPY cas_server/__init__.py ./customer_analysis_service

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
