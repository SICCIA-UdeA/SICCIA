// Contrato del JSON "configurador" que espera POST /orquestador/cursos.
// Refleja BackEnd/app/orquestador/schemas.py (Configurador); mantener sincronizado.

export type ModuloConfig = { titulo: string; temas: string[] };

export type DatosCurso = {
  tema: string;
  publico_objetivo: string | null;
  duracion_estimada: string | null;
  metodologia: string | null;
};

export type ContenidoConfig = {
  modulos_modo: "automatico" | "manual";
  num_modulos: number | null;
  modulos: ModuloConfig[];
  incluir_ejemplos_practicos: boolean;
  incluir_talleres_practica: boolean;
  incluir_cierre_por_modulo: boolean;
};

export type ActividadEvaluativa = { tipo: string; cantidad: number; porcentaje: number | null };

export type EvaluacionConfig = {
  tipos_pregunta: string[];
  actividades: ActividadEvaluativa[];
  total_actividades: number | null;
};

export type EstiloConfig = { formato_salida: string; incluir_imagenes: boolean };

export type Configurador = {
  datos: DatosCurso;
  contenido: ContenidoConfig;
  evaluacion: EvaluacionConfig;
  estilo: EstiloConfig;
};

export const MAX_MODULOS = 20;
export const MIN_TEMA = 3;

export type EstadoFormulario = {
  tema: string;
  publico: string;
  duracion: string;
  metodologia: string;
  modulos: string[];
  ejemplos: boolean;
  talleres: boolean;
  cierre: boolean;
  tiposPregunta: string[];
  actividades: Array<{ tipo: string; cantidad: number; porcentaje: number | null }>;
  imagenes: boolean;
};

const limpio = (s: string) => s.trim();
const opcional = (s: string) => (limpio(s) ? limpio(s) : null);

export function construirConfigurador(f: EstadoFormulario): Configurador {
  const modulos = f.modulos.map(limpio).filter(Boolean).map((titulo) => ({ titulo, temas: [] }));
  const actividades = f.actividades.map((a) => ({
    tipo: limpio(a.tipo),
    cantidad: Math.max(1, Math.trunc(a.cantidad) || 1),
    porcentaje: a.porcentaje,
  }));
  const total = actividades.reduce((s, a) => s + a.cantidad, 0);
  return {
    datos: {
      tema: limpio(f.tema),
      publico_objetivo: opcional(f.publico),
      duracion_estimada: opcional(f.duracion),
      metodologia: opcional(f.metodologia),
    },
    contenido: {
      modulos_modo: modulos.length ? "manual" : "automatico",
      num_modulos: modulos.length || null,
      modulos,
      incluir_ejemplos_practicos: f.ejemplos,
      incluir_talleres_practica: f.talleres,
      incluir_cierre_por_modulo: f.cierre,
    },
    evaluacion: {
      tipos_pregunta: f.tiposPregunta,
      actividades,
      total_actividades: total || null,
    },
    estilo: { formato_salida: "pdf", incluir_imagenes: f.imagenes },
  };
}

// Replica las validaciones de Pydantic para no enviar un JSON que el back rechace (422).
export function validarConfigurador(c: Configurador): string[] {
  const errores: string[] = [];
  if (c.datos.tema.length < MIN_TEMA) errores.push(`El nombre del curso debe tener al menos ${MIN_TEMA} caracteres.`);
  if (c.contenido.modulos.length > MAX_MODULOS) errores.push(`Máximo ${MAX_MODULOS} módulos.`);
  if (c.evaluacion.actividades.some((a) => a.tipo.length < 2)) errores.push("Cada actividad evaluativa necesita un tipo.");
  const dados = c.evaluacion.actividades.map((a) => a.porcentaje).filter((p): p is number => p !== null);
  if (dados.some((p) => p < 0 || p > 100)) errores.push("Cada porcentaje debe estar entre 0 y 100.");
  const suma = dados.reduce((s, p) => s + p, 0);
  if (suma > 100.01) errores.push(`Los porcentajes suman ${suma}%, máximo 100%.`);
  else if (c.evaluacion.actividades.length && dados.length === c.evaluacion.actividades.length && Math.abs(suma - 100) > 0.01)
    errores.push(`Los porcentajes suman ${suma}%, deben sumar 100%.`);
  return errores;
}

export function descargarJson(data: unknown, nombre: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nombre;
  a.click();
  URL.revokeObjectURL(url);
}

export function nombreArchivo(tema: string) {
  const slug = tema
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_|_$/g, "")
    .slice(0, 50);
  return `configurador_${slug || "curso"}.json`;
}
