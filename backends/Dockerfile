# Init
FROM python:3.10.7
WORKDIR /usr/src/backends

# Ensure Start Up Order
# https://docs.docker.com/compose/startup-order/
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Install packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Cache CLIP model
# RUN mkdir -p /.cache/clip
# RUN wget -O /.cache/clip/ViT-L-14-336px.pt "https://openaipublic.azureedge.net/clip/models/3035c92b350959924f9f00213499208652fc7ea050643e8b385c2dac08641f02/ViT-L-14-336px.pt"

# Copy src
COPY . .

# Start
EXPOSE 3000
CMD ["python", "-u", "src/server.py"]
 