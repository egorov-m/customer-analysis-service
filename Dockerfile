FROM python:3.11.3

WORKDIR /app

COPY ./requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY ./main.py .
COPY ./customer_analysis_service/api ./customer_analysis_service
COPY ./customer_analysis_service/db/models ./customer_analysis_service/db
COPY ./customer_analysis_service/db/repository ./customer_analysis_service/db
COPY ./customer_analysis_service/db/database.py ./customer_analysis_service/db
COPY ./customer_analysis_service/db/__init__.py ./customer_analysis_service/db
COPY ./customer_analysis_service/services/analysis ./customer_analysis_service/services
COPY ./customer_analysis_service/services/__init__.py ./customer_analysis_service/services
COPY ./customer_analysis_service/config.py ./customer_analysis_service
COPY ./customer_analysis_service/__init__.py ./customer_analysis_service

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
