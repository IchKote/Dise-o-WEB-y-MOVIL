FROM node:22-slim

ENV NODE_ENV=production
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

COPY src src
USER node

EXPOSE 8100
CMD ["node", "src/server.js"]
