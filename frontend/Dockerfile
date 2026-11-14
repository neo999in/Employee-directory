FROM node:20-alpine

WORKDIR /app

# Copy package definitions first for layer caching
COPY package*.json ./

# Install dependencies inside Linux container
RUN npm install

# Copy application source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

ENV VITE_API_BASE_URL=http://localhost:8000/api

CMD ["npm", "run", "dev", "--", "--host"]
