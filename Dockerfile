FROM python:3
RUN mkdir /app
WORKDIR /app
ADD model.py /app/model.py
ADD requirements.txt /app/requirements.txt

RUN python3 -m pip install -r requirements.txt
RUN chmod +x /app/model.py
ENTRYPOINT ["/app/model.py"]
