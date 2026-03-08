import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,  // 监听所有网络接口，允许局域网访问
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        timeout: 600000,
        proxyTimeout: 600000,
        // 关键：禁用响应缓冲，让 NDJSON 流式数据实时穿透到浏览器
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes) => {
            // 强制禁用任何缓冲层，立即透传每个数据块
            proxyRes.headers['x-accel-buffering'] = 'no';
          });
        },
      },
    },
  },
})

