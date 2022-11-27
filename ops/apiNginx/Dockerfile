FROM nginx:1.9

# Install curl for helping setup environment variables
RUN apt-get update && apt-get install -y --no-install-recommends --force-yes curl \
      && rm -rf /var/lib/apt/lists/*

# Delete the default welcome to nginx page.
RUN rm /usr/share/nginx/html/*

# Overwrite nginx config with custom
COPY configs/nginx.conf /etc/nginx/nginx.conf
COPY configs/default.conf /etc/nginx/conf.d/default.conf

# Modify environment variables for production API containers.
# Update permissions so script can be run
COPY docker-entrypoint.sh /
RUN chmod 755 /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
