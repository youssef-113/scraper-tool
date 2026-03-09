FROM python:3.11

WORKDIR /app

# Force upgrade pip
RUN pip install --upgrade pip

# Force reinstall scrapling with fetchers
RUN pip install --no-cache-dir --upgrade --force-reinstall "scrapling[fetchers]"

RUN scrapling install

COPY . .

CMD ["bash"]