// @lovable.dev/vite-tanstack-config already includes the following — do NOT add them manually
// or the app will break with duplicate plugins:
//   - TanStack devtools (dev-only, first), tanstackStart, viteReact, tailwindcss, tsConfigPaths,
//     nitro (build-only using cloudflare as a default target), VITE_* env injection, @ path alias,
//     React/TanStack dedupe, error logger plugins, and sandbox detection (port/host/strictPort).
// You can pass additional config via defineConfig({ vite: { ... }, etc... }) if needed.
import { defineConfig } from "@lovable.dev/vite-tanstack-config";
import { loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  // process.env contains exported variables; loadEnv reads the frontend .env files.
  // BACKEND_* therefore resolve from process.env, then frontend .env, then local defaults.
  const env = loadEnv(mode, process.cwd(), "");
  const backendPort = Number.parseInt(process.env["BACKEND_PORT"] ?? env["BACKEND_PORT"] ?? "8084", 10);
  const frontendPort = Number.parseInt(process.env["FRONTEND_PORT"] ?? env["FRONTEND_PORT"] ?? "8085", 10);
  return {
  tanstackStart: {
    // Redirect TanStack Start's bundled server entry to src/server.ts (our SSR error wrapper).
    // nitro/vite builds from this
    server: { entry: "server" },
  },
  vite: {
    define: {
      "import.meta.env.VITE_BACKEND_PORT": JSON.stringify(String(backendPort)),
      "import.meta.env.VITE_FRONTEND_PORT": JSON.stringify(String(frontendPort)),
    },
    server: {
      port: frontendPort,
      strictPort: true,
      proxy: {
        // Reenvía /api/* al backend unificado sin requerir CORS.
        "/api": {
          target: process.env["BACKEND_URL"] ?? env["BACKEND_URL"] ?? `http://127.0.0.1:${backendPort}`,
          // Flask arma la redirect_uri de Google con este Host; debe coincidir con la registrada
          // en Google Cloud (http://localhost:8084/auth/google/callback) y con el host del front.
          changeOrigin: false,
          headers: { host: process.env["BACKEND_HOST"] ?? env["BACKEND_HOST"] ?? `localhost:${backendPort}` },
          rewrite: (path) => path.replace(/^\/api/, ""),
        },
      },
    },
  },
  };
});
