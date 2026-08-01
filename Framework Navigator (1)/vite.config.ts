// @lovable.dev/vite-tanstack-config already includes the following — do NOT add them manually
// or the app will break with duplicate plugins:
//   - TanStack devtools (dev-only, first), tanstackStart, viteReact, tailwindcss, tsConfigPaths,
//     nitro (build-only using cloudflare as a default target), VITE_* env injection, @ path alias,
//     React/TanStack dedupe, error logger plugins, and sandbox detection (port/host/strictPort).
// You can pass additional config via defineConfig({ vite: { ... }, etc... }) if needed.
import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  server: {
    host: true,
    allowedHosts: ["f37c550e5cd024.lhr.life", ".lhr.life", "lhr.life", ".localhost.run", "localhost.run", ".pinggy.link", "localhost", "127.0.0.1"],
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
    preset: "firebase-app-hosting",
  },
  vite: {
    server: {
      host: true,
      allowedHosts: ["f37c550e5cd024.lhr.life", ".lhr.life", "lhr.life", ".localhost.run", "localhost.run", ".pinggy.link", "localhost", "127.0.0.1"],
      proxy: {
        "/recommend": "http://localhost:8000",
        "/profiles": "http://localhost:8000",
        "/frameworks": "http://localhost:8000",
      },
    },
  },
});
