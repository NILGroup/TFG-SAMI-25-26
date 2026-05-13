import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
      manifest: {
        name: 'SAMI - Asistente Virtual UCM',
        short_name: 'SAMI',
        description: 'Sistema Accesible para la Mejora a la Inclusión',
        theme_color: '#8D0D19',
        background_color: '#f4f4f4',
        display: 'standalone',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: 'sami_192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'sami_512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'sami_512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^http:\/\/127\.0\.0\.1:5555\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 10,
            }
          }
        ]
      }
    })
  ],
})