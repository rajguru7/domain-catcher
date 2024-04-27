# Use the official Nginx image as the base
FROM nginx:latest

# Set the working directory inside the container
WORKDIR /usr/share/nginx/html

# Remove the default Nginx index.html file
RUN rm index.html

# Copy the local index.html file into the container
COPY ./index.html .

# The container listens on port 80 by default, so no need to expose it

# When the container starts, it will run Nginx, and Nginx will respond to web requests

