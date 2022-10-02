# Init
FROM python:3.10.7-bullseye
WORKDIR /usr/src/backends

# Ensure Start Up Order
# https://docs.docker.com/compose/startup-order/
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Copy src
COPY . .

# Install packages
RUN pip install -r requirements.txt

# Start
EXPOSE 3000
CMD ["python", "-u", "src/server.py"]
 