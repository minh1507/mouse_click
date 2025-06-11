FROM node:18-alpine

WORKDIR /app

# Sao chép package.json và package-lock.json
COPY package*.json ./

# Cài đặt các phụ thuộc
RUN npm ci

# Sao chép mã nguồn
COPY . .

# Build ứng dụng
RUN npm run build

# Mở port
EXPOSE 3000

# Khởi động ứng dụng
CMD ["npm", "start"] 