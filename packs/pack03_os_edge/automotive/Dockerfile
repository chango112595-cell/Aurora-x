FROM python:3.11-slim
WORKDIR /app
COPY automotive/ /app/automotive/
RUN pip install python-can udsoncan isotp
CMD ["python3","/app/automotive/can_bridge.py"]
