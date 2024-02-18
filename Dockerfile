# pull a Python 3.12 version
FROM python:3.12.1

# install everything
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm requirements.txt

# create a folder for the application
RUN mkdir /app
COPY ./storage /app/storage

# set the working directory
WORKDIR /app

# run the application
EXPOSE 8000
CMD ["uvicorn", "storage.app:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]