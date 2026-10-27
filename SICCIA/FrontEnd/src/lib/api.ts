// Cliente HTTP del orquestador (BackEnd/controller/orquestador_controller.py).
// En desarrollo las llamadas van a "/api" y el proxy de Vite las reenvía al backend,
// así se evita CORS (el backend no lo tiene configurado).
import type { Configurador } from "./configurador";
import { crearZip } from "./zip";

const BASE = (import.meta.env["VITE_API_URL"] as string | undefined)?.replace(/\/$/, "") || "/api";

export type EstadoTrabajo = "pendiente" | "planificando" | "ejecutando" | "completado" | "completado_con_errores" | "error";

export type ArchivoInfo = { nombre: string; via: string; tamano_bytes: number };

export type TrabajoCreado = { id: string; estado: EstadoTrabajo };

export type TrabajoRespuesta = {
  id: string;
  estado: EstadoTrabajo;
  creado_en: string;
  vias: Record<string, string>;
  archivos: ArchivoInfo[];
  error: string | null;
};

export const ESTADOS_FINALES: EstadoTrabajo[] = ["completado", "completado_con_errores", "error"];

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
  }
}

type DetalleValidacion = { loc?: Array<string | number>; msg?: string };

async function leerError(res: Response): Promise<ApiError> {
  let mensaje = [502, 503, 504].includes(res.status)
    ? "No se pudo conectar con el backend. Verifica que esté corriendo en el puerto 8080."
    : `Error ${res.status} del servidor`;
  try {
    const body = (await res.json()) as { detail?: string | DetalleValidacion[] };
    if (typeof body.detail === "string") mensaje = body.detail;
    else if (Array.isArray(body.detail))
      mensaje = body.detail.map((d) => `${(d.loc ?? []).filter((x) => x !== "body").join(".")}: ${d.msg ?? ""}`).join(" | ");
  } catch {
    // Respuesta sin JSON: se conserva el mensaje genérico.
  }
  return new ApiError(mensaje, res.status);
}

async function pedir<T>(ruta: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${ruta}`, { credentials: "include", ...init });
  } catch {
    throw new ApiError("No se pudo conectar con el backend. Verifica que esté corriendo en el puerto 8080.", 0);
  }
  if (!res.ok) throw await leerError(res);
  return (await res.json()) as T;
}

export function crearCurso(config: Configurador, signal?: AbortSignal) {
  return pedir<TrabajoCreado>("/orquestador/cursos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
    signal: signal ?? null,
  });
}

export function estadoCurso(id: string, signal?: AbortSignal) {
  return pedir<TrabajoRespuesta>(`/orquestador/cursos/${encodeURIComponent(id)}`, { signal: signal ?? null });
}

async function descargarBlob(ruta: string, nombre: string) {
  let res: Response;
  try {
    res = await fetch(`${BASE}${ruta}`, { credentials: "include" });
  } catch {
    throw new ApiError("No se pudo conectar con el backend.", 0);
  }
  if (!res.ok) throw await leerError(res);
  guardarBlob(await res.blob(), nombre);
}

function guardarBlob(blob: Blob, nombre: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nombre;
  a.click();
  URL.revokeObjectURL(url);
}

// Arma el .zip en el navegador solo con los PDF, descargando cada uno desde
// /orquestador/cursos/{id}/archivos/{nombre}. No usa el endpoint /descarga del backend,
// que empaqueta también los .md.
export async function descargarZipPdf(id: string, nombres: string[]) {
  if (!nombres.length) throw new ApiError("El trabajo no tiene archivos PDF para descargar.", 404);
  const entradas = await Promise.all(
    nombres.map(async (nombre) => {
      let res: Response;
      try {
        res = await fetch(`${BASE}/orquestador/cursos/${encodeURIComponent(id)}/archivos/${encodeURIComponent(nombre)}`, { credentials: "include" });
      } catch {
        throw new ApiError("No se pudo conectar con el backend.", 0);
      }
      if (!res.ok) throw await leerError(res);
      return { nombre, datos: new Uint8Array(await res.arrayBuffer()) };
    }),
  );
  guardarBlob(crearZip(entradas), `curso_${id.slice(0, 8)}.zip`);
}

export function descargarArchivo(id: string, nombre: string) {
  return descargarBlob(`/orquestador/cursos/${encodeURIComponent(id)}/archivos/${encodeURIComponent(nombre)}`, nombre);
}

// --- Autenticación con Google (BackEnd/controller/auth_controller.py) ---
export type Usuario = { id: string; name: string | null; email: string | null; picture: string | null };

type RespuestaMe = { authenticated: boolean } & Partial<Usuario>;

export async function usuarioActual(signal?: AbortSignal): Promise<Usuario | null> {
  let res: Response;
  try {
    res = await fetch(`${BASE}/auth/me`, { credentials: "include", signal: signal ?? null });
  } catch {
    throw new ApiError("No se pudo conectar con el backend. Verifica que esté corriendo en el puerto 8080.", 0);
  }
  if (res.status === 401) return null;
  if (!res.ok) throw await leerError(res);
  const body = (await res.json()) as RespuestaMe;
  if (!body.authenticated || !body.id) return null;
  return { id: body.id, name: body.name ?? null, email: body.email ?? null, picture: body.picture ?? null };
}

export const urlLoginGoogle = () => `${BASE}/auth/google`;

export async function cerrarSesion() {
  try {
    await fetch(`${BASE}/auth/logout`, { credentials: "include" });
  } catch {
    // Si el backend no responde, la sesión local se limpia igual.
  }
}
