FROM node:18-alpine

# Install system dependencies
RUN apk add --no-cache python3 make g++ git

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S blockchain && \
    adduser -S blockchain -u 1001 -G blockchain

# Create directories
RUN mkdir -p /app/build /app/migrations /app/contracts && \
    chown -R blockchain:blockchain /app

USER blockchain

# Expose ports
EXPOSE 8545 8546

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8545 || exit 1

# Start the blockchain node
CMD ["npm", "start"]
