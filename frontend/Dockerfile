# Use node as the base image
FROM node:22-alpine AS build

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY frontend-app/package.json frontend-app/package-lock.json ./
RUN npm install

# Copy the entire app and build
COPY frontend-app ./
RUN npm run build

# Production environment using nginx
FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY frontend-app/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
