FROM node:20-alpine

WORKDIR /app

# Copy package config and install dependencies
COPY package.json ./
RUN npm install

# Copy frontend source
COPY . .

# Expose Vite's default port
EXPOSE 5173

# Start Vite dev server and expose host for Docker networking
CMD ["npm", "run", "dev", "--", "--host"]
