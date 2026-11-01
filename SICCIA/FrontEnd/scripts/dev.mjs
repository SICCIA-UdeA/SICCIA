import { createServer, loadConfigFromFile, loadEnv } from "vite";

const env = loadEnv("development", process.cwd(), "");
const port = Number.parseInt(process.env["FRONTEND_PORT"] ?? env["FRONTEND_PORT"] ?? "8085", 10);

if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error("FRONTEND_PORT debe ser un puerto válido entre 1 y 65535.");
}

const loaded = await loadConfigFromFile({ command: "serve", mode: "development" }, "vite.config.ts");
if (!loaded) {
  throw new Error("No se pudo cargar vite.config.ts.");
}

const { vite: extraViteConfig, tanstackStart: _tanstackStart, ...baseViteConfig } = loaded.config;
const server = await createServer({
  ...baseViteConfig,
  ...extraViteConfig,
  configFile: false,
  define: { ...baseViteConfig.define, ...extraViteConfig?.define },
  resolve: { ...baseViteConfig.resolve, ...extraViteConfig?.resolve },
  server: {
    ...baseViteConfig.server,
    ...extraViteConfig?.server,
    host: "localhost",
    port,
    strictPort: true,
    proxy: { ...baseViteConfig.server?.proxy, ...extraViteConfig?.server?.proxy },
  },
});

await server.listen();
server.printUrls();

const cerrar = async () => {
  await server.close();
  process.exit(0);
};

process.on("SIGINT", () => void cerrar());
process.on("SIGTERM", () => void cerrar());
