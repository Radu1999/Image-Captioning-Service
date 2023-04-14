# Use the latest version of the official Redis image as the base image
FROM redis:latest

# Set an environment variable to configure Redis to run as a standalone server
ENV REDIS_MODE standalone

# Expose the Redis port
EXPOSE 6379

# Copy the Redis configuration file to the container
COPY redis.conf /usr/local/etc/redis/redis.conf

# Start Redis using the configuration file
CMD [ "redis-server", "/usr/local/etc/redis/redis.conf" ]
