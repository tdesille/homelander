FROM python:3.12-slim

WORKDIR /app

COPY ./dist/homelander-0.1.0-py3-none-any.whl .
RUN pip install --no-cache-dir homelander-0.1.0-py3-none-any.whl

EXPOSE 8501

CMD ["streamlit", "run", "--server.address=0.0.0.0", "/usr/local/lib/python3.12/site-packages/homelander/main.py"]