FROM python:3.10.6
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ .
CMD ["python", "./controller.py"]