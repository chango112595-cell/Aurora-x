import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import runtimeErrorOverlay from "@replit/vite-plugin-runtime-error-modal";

export default defineConfig({
  plugins: [
    react(),
    runtimeErrorOverlay(),
    ...(process.env.NODE_ENV !== "production" &&
      process.env.REPL_ID !== undefined
      ? [
        await import("@replit/vite-plugin-cartographer").then((m) =>
          m.cartographer(),
        ),
        await import("@replit/vite-plugin-dev-banner").then((m) =>
          m.devBanner(),
        ),
      ]
      : []),
  ],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "client", "src"),
      "@shared": path.resolve(import.meta.dirname, "shared"),
      "@assets": path.resolve(import.meta.dirname, "attached_assets"),
    },
  },
  root: path.resolve(import.meta.dirname, "client"),
  build: {
    outDir: path.resolve(import.meta.dirname, "dist/public"),
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: `assets/[name].[hash].js`,
        chunkFileNames: `assets/[name].[hash].js`,
        assetFileNames: `assets/[name].[hash].[ext]`
      }
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: [
      '.replit.dev',
      '.repl.co',
      '.app.github.dev',
      '.preview.app.github.dev',
    ],
    proxy: {
      '/api/chat': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('Proxy error for /api/chat:', err.message);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Proxying /api/chat request to localhost:5003');
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('Response from localhost:5003, status:', proxyRes.statusCode);
          });
        },
      },
      '/api/status': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/api/bridge': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://localhost:5002',
        changeOrigin: true,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('Proxy error for /api:', err.message);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Proxying /api request to localhost:5002');
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('Response from localhost:5002, status:', proxyRes.statusCode);
          });
        },
      },
    },
    fs: {
      strict: true,
      deny: ["**/.*"],
    },
    hmr: {
      timeout: 30000,
      overlay: false,
      // For Codespaces/GitHub dev containers
      host: 'localhost',
      port: 5173,
    },
    watch: {
      usePolling: false,
      interval: 1000,
    },
  },
});
