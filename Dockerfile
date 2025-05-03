FROM python:3.11-slim

# Install dependencies: curl and speedtest cli (https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh)
RUN apt-get update && \
  apt-get install -y curl && \
  curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash && \
  apt-get install -y speedtest-cli


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]
