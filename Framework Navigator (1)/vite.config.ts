import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  server: {
    host: true,
    proxy: {
      "/recommend": "http://localhost:8000",
      "/profiles": "http://localhost:8000",
      "/frameworks": "http://localhost:8000",
    },
  },
  tanstackStart: {
    // Redirect TanStack Start's bundled server entry to src/server.ts (our SSR error wrapper).
    // nitro/vite builds from this
    server: { entry: "server" },
  },
  nitro: {
    preset: process.env.BUILD_TARGET === "render" ? "node-server" : (process.env.BUILD_TARGET === "firebase" ? "firebase-app-hosting" : undefined),
  },
  vite: {
    server: {
      host: true,
      proxy: {
        "/recommend": "http://localhost:8000",
        "/profiles": "http://localhost:8000",
        "/frameworks": "http://localhost:8000",
      },
    },
  },
});
