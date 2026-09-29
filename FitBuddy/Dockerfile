FROM python:3.12-slim
WORKDIR /srv
ENV PYTHONUNBUFFERED=1 HOST=0.0.0.0 RELOAD=false DATABASE_URL=sqlite:////data/fitbuddy.db
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /data
VOLUME /data
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
