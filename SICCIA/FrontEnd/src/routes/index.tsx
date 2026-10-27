import { createFileRoute } from "@tanstack/react-router";
import {
  Bell, BookOpen, Bot, Check, ChevronDown, ChevronRight, CircleAlert,
  Download, FileText, LayoutDashboard,
  LogOut, Menu, Plus, ShieldCheck, Sparkles, User, X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { cerrarSesion, crearCurso, descargarArchivo, descargarZipPdf, ESTADOS_FINALES, estadoCurso, urlLoginGoogle, usuarioActual, type EstadoTrabajo, type TrabajoRespuesta, type Usuario } from "@/lib/api";
import { type Configurador, construirConfigurador, MAX_MODULOS, MIN_TEMA, validarConfigurador } from "@/lib/configurador";

export const Route = createFileRoute("/")({
  head: () => ({ meta: [
    { title: "SICCIA — Panel docente" },
    { name: "description", content: "Crea, verifica y descarga cursos educativos estructurados con inteligencia artificial." },
    { property: "og:title", content: "SICCIA — Panel docente" },
    { property: "og:description", content: "Generación de cursos con IA, control de calidad y supervisión docente." },
    { property: "og:type", content: "website" },
    { name: "twitter:card", content: "summary_large_image" },
  ] }),
  component: Index,
});

type View = "dashboard" | "courses" | "generator" | "settings" | "result";
type AuthStage = "welcome" | "login";

const courses = [
  { initials: "JV", title: "Lenguaje de programación Java", meta: "Secundaria · 16 h · Learning to do", status: "Generado", tone: "success", progress: 100 },
  { initials: "FR", title: "Fracciones para Básica Primaria", meta: "Primaria · 6 h · Resolución de problemas", status: "En revisión de calidad", tone: "warning", progress: 72 },
  { initials: "EA", title: "Ecosistemas andinos y biodiversidad", meta: "Primaria · 4 h · Aprendizaje por proyectos", status: "Pendiente de aprobación", tone: "muted", progress: 38 },
];


function Logo() {
  return <div className="flex items-center gap-2"><span className="grid size-9 place-items-center rounded-lg bg-primary text-sm font-bold text-primary-foreground shadow-sm">S</span><span className="font-bold text-foreground">SICCIA</span></div>;
}

function V2Mark({ children, className, label = "Para versión 2.0" }: { children: React.ReactNode; className?: string; label?: string }) {
  return <div className={cn("relative", className)} aria-disabled="true" title={label}>
    <div inert className="pointer-events-none h-full select-none opacity-40">{children}</div>
    <div className="pointer-events-none absolute inset-0 grid place-items-center overflow-hidden rounded-xl"><span className="-rotate-12 rounded-md border-2 border-primary/40 bg-surface/80 px-3 py-1 text-xs font-bold uppercase tracking-wider text-primary sm:text-sm">{label}</span></div>
  </div>;
}

function Index() {
  const [user, setUser] = useState<Usuario | null>(null);
  const [checking, setChecking] = useState(true);
  const [view, setView] = useState<View>("dashboard");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [noticeOpen, setNoticeOpen] = useState(false);
  useEffect(() => {
    const ctrl = new AbortController();
    usuarioActual(ctrl.signal).then(u => setUser(u)).catch(() => setUser(null)).finally(() => { if (!ctrl.signal.aborted) setChecking(false); });
    return () => ctrl.abort();
  }, []);
  const logout = async () => { await cerrarSesion(); setUser(null); setView("dashboard"); };
  if (checking) return <main className="grid min-h-screen place-items-center bg-background"><div className="flex flex-col items-center gap-3"><Logo /><p className="text-sm text-muted-foreground">Verificando sesión...</p></div></main>;
  if (!user) return <AuthScreen onLogin={u => { setUser(u); setView("dashboard"); }} />;
  return <AppShell user={user} view={view} setView={setView} mobileMenu={mobileMenu} setMobileMenu={setMobileMenu} collapsed={collapsed} setCollapsed={setCollapsed} noticeOpen={noticeOpen} setNoticeOpen={setNoticeOpen} onLogout={() => void logout()} />;
}

const DEMO_USER: Usuario = { id: "demo", name: "Docente de Prueba", email: "prueba@siccia.local", picture: null };
const isDemo = (u: Usuario) => u.id === DEMO_USER.id;
const LOGIN_POLL_MS = 1500;
const LOGIN_TIMEOUT_MS = 5 * 60 * 1000;

function AuthScreen({ onLogin }: { onLogin: (u: Usuario) => void }) {
  const [stage, setStage] = useState<AuthStage>("welcome");
  const [waiting, setWaiting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const popupRef = useRef<Window | null>(null);
  const timerRef = useRef<number | undefined>(undefined);
  const wrongHost = typeof window !== "undefined" && window.location.hostname === "127.0.0.1";
  useEffect(() => () => { window.clearTimeout(timerRef.current); popupRef.current?.close(); }, []);
  const stop = (msg: string | null) => { window.clearTimeout(timerRef.current); setWaiting(false); setError(msg); };
  const loginGoogle = () => {
    setError(null);
    const popup = window.open(urlLoginGoogle(), "siccia-google", "width=500,height=650");
    if (!popup) { window.location.href = urlLoginGoogle(); return; }
    popupRef.current = popup;
    setWaiting(true);
    const started = Date.now();
    const tick = async () => {
      try {
        const u = await usuarioActual();
        if (u) { popup.close(); stop(null); onLogin(u); return; }
      } catch (e) {
        popup.close(); stop(e instanceof Error ? e.message : "No se pudo verificar la sesión."); return;
      }
      if (popup.closed) { stop("No se completó el inicio de sesión. Intenta de nuevo."); return; }
      if (Date.now() - started > LOGIN_TIMEOUT_MS) { popup.close(); stop("El inicio de sesión tardó demasiado. Intenta de nuevo."); return; }
      timerRef.current = window.setTimeout(() => void tick(), LOGIN_POLL_MS);
    };
    timerRef.current = window.setTimeout(() => void tick(), LOGIN_POLL_MS);
  };
  return <main className="relative grid min-h-screen place-items-center overflow-hidden bg-background px-4 py-10">
    <div className="absolute inset-x-0 top-0 h-1 bg-primary" />
    <div className="absolute left-[8%] top-[10%] size-72 rounded-full bg-primary-soft/70 blur-3xl" />
    {stage === "welcome" ? <section className="glass-panel relative z-10 w-full max-w-lg rounded-2xl p-8 text-center sm:p-10">
      <div className="mb-8 flex justify-center"><Logo /></div>
      <h1 className="text-3xl font-bold">Bienvenidos a SICCIA</h1>
      <p className="mx-auto mt-3 max-w-sm text-sm text-muted-foreground">Sistema para crear cursos educativos estructurados con inteligencia artificial y criterio pedagógico.</p>
      <Button className="mt-8 w-full sm:w-auto sm:px-8" onClick={() => setStage("login")}>Ingresar<ChevronRight className="size-4"/></Button>
    </section> : <section className="glass-panel relative z-10 w-full max-w-md rounded-2xl p-6 text-center sm:p-8">
      <div className="mb-8 flex justify-center"><Logo /></div>
      <h1 className="text-2xl font-bold">Inicia sesión</h1>
      <p className="mt-2 text-sm text-muted-foreground">Usa tu cuenta de Google para ingresar.</p>
      <Button variant="outline" className="mt-8 h-11 w-full border-border bg-surface text-foreground shadow-sm hover:bg-muted hover:text-foreground" disabled={waiting} onClick={loginGoogle}><GoogleMark className="size-4"/>{waiting ? "Esperando a Google..." : "Iniciar sesión con Google"}</Button>
      {waiting && <p className="mt-3 text-xs text-muted-foreground">Completa el inicio de sesión en la ventana de Google.</p>}
      <div className="mt-6 flex items-center gap-3"><span className="h-px flex-1 bg-border"/><span className="text-xs text-muted-foreground">solo para pruebas</span><span className="h-px flex-1 bg-border"/></div>
      <Button variant="ghost" className="mt-3 w-full border border-dashed border-border text-muted-foreground" disabled={waiting} onClick={() => onLogin(DEMO_USER)}>Acceso simulado</Button>
      {error && <p className="mt-3 text-xs text-destructive">{error}</p>}
      {wrongHost && <p className="mt-3 rounded-lg bg-warning-soft p-2 text-xs text-muted-foreground">Abre la aplicación en <b>http://localhost:5173</b> para que el inicio de sesión funcione.</p>}
      <button type="button" className="mt-6 text-xs font-semibold text-primary hover:underline" onClick={() => { stop(null); popupRef.current?.close(); setStage("welcome"); }}>Volver</button>
    </section>}
  </main>;
}

function GoogleMark({ className }: { className?: string }) {
  return <svg className={className} viewBox="0 0 24 24" aria-hidden="true"><path fill="#4285F4" d="M23.5 12.27c0-.85-.08-1.66-.22-2.45H12v4.64h6.45a5.52 5.52 0 0 1-2.39 3.62v3h3.87c2.26-2.09 3.57-5.16 3.57-8.81Z"/><path fill="#34A853" d="M12 24c3.24 0 5.96-1.07 7.94-2.91l-3.87-3c-1.08.72-2.45 1.15-4.07 1.15-3.13 0-5.78-2.11-6.73-4.96H1.29v3.1A12 12 0 0 0 12 24Z"/><path fill="#FBBC05" d="M5.27 14.28a7.2 7.2 0 0 1 0-4.56v-3.1H1.29a12 12 0 0 0 0 10.76l3.98-3.1Z"/><path fill="#EA4335" d="M12 4.76c1.76 0 3.34.6 4.58 1.79l3.44-3.44A11.98 11.98 0 0 0 12 0 12 12 0 0 0 1.29 6.62l3.98 3.1C6.22 6.87 8.87 4.76 12 4.76Z"/></svg>;
}

function Field({ label, ...props }: { label: string } & React.InputHTMLAttributes<HTMLInputElement>) {
  return <label className="block"><span className="mb-1.5 block text-sm font-medium">{label}</span><input className="h-11 w-full rounded-lg border border-input bg-surface px-3 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/15" required {...props}/></label>;
}

const nav = [
  ["dashboard", "Panel principal", LayoutDashboard], ["courses", "Mis cursos", BookOpen], ["generator", "Generar nuevo curso", Sparkles], ["settings", "Información personal", User],
] as const;

function displayName(u: Usuario) { return u.name?.trim() || u.email || "Docente"; }
function shortName(u: Usuario) {
  const parts = displayName(u).split(/\s+/).filter(Boolean);
  const next = parts.slice(1).find(w => /^\p{Lu}/u.test(w));
  return next && !displayName(u).includes("@") ? `${parts[0]} ${next[0]}.` : parts[0] ?? displayName(u);
}
function initials(u: Usuario) {
  const parts = displayName(u).split(/[\s@.]+/).filter(Boolean);
  const next = parts.slice(1).find(w => /^\p{Lu}/u.test(w)) ?? parts[1];
  return ((parts[0]?.[0] ?? "") + (next?.[0] ?? "")).toUpperCase() || "D";
}
function UserAvatar({ user }: { user: Usuario }) {
  const [failed, setFailed] = useState(false);
  if (user.picture && !failed) return <img src={user.picture} alt="" referrerPolicy="no-referrer" onError={() => setFailed(true)} className="size-8 rounded-md object-cover"/>;
  return <span className="grid size-8 place-items-center rounded-md bg-primary-soft text-xs font-bold text-primary">{initials(user)}</span>;
}

function AppShell(props: { user: Usuario; view: View; setView: (v: View) => void; mobileMenu: boolean; setMobileMenu: (v: boolean) => void; collapsed: boolean; setCollapsed: (v: boolean) => void; noticeOpen: boolean; setNoticeOpen: (v: boolean) => void; onLogout: () => void }) {
  const { user, view, setView, mobileMenu, setMobileMenu, collapsed, setCollapsed, noticeOpen, setNoticeOpen, onLogout } = props;
  const title = ({ dashboard: "Panel principal", courses: "Mis cursos", generator: "Generar nuevo curso", settings: "Información personal", result: "Curso generado" } as const)[view];
  const [job, setJob] = useState<TrabajoRespuesta | null>(null);
  const [jobConfig, setJobConfig] = useState<Configurador | null>(null);
  const go = (v: View) => { setView(v); setMobileMenu(false); };
  return <div className="min-h-screen bg-background text-foreground">
    {mobileMenu && <button aria-label="Cerrar menú" className="fixed inset-0 z-30 bg-foreground/20 lg:hidden" onClick={() => setMobileMenu(false)} />}
    <aside className={cn("fixed inset-y-0 left-0 z-40 flex flex-col border-r border-border bg-surface/95 p-3 backdrop-blur-xl transition-[width,transform] lg:translate-x-0", mobileMenu ? "translate-x-0" : "-translate-x-full", collapsed ? "w-20" : "w-64")}>
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center px-2 py-2"><div className={cn("min-w-0 overflow-hidden", collapsed && "lg:w-9")}><Logo /></div><Button className="lg:hidden" size="icon" variant="ghost" onClick={() => setMobileMenu(false)} aria-label="Cerrar menú"><X className="size-5"/></Button></div>
      <nav className="mt-5 space-y-1">{nav.map(([id, label, Icon]) => <button key={id} onClick={() => go(id)} title={label} className={cn("flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors", view === id ? "bg-primary-soft text-primary" : "text-muted-foreground hover:bg-muted hover:text-foreground", collapsed && "lg:justify-center lg:px-0")}><Icon className="size-4 shrink-0"/><span className={cn("truncate", collapsed && "lg:hidden")}>{label}</span></button>)}</nav>
      <Button className="mt-auto w-full" variant="ghost" onClick={onLogout}><LogOut className="size-4"/><span className={cn(collapsed && "lg:hidden")}>Cerrar sesión</span></Button>
      <Button className="absolute -right-4 top-20 hidden rounded-full bg-surface shadow-sm lg:inline-flex" size="icon" variant="secondary" onClick={() => setCollapsed(!collapsed)} aria-label={collapsed ? "Expandir menú" : "Contraer menú"}><ChevronRight className={cn("size-4 transition-transform", !collapsed && "rotate-180")}/></Button>
    </aside>
    <div className={cn("transition-[margin]", collapsed ? "lg:ml-20" : "lg:ml-64")}>
      <header className="sticky top-0 z-20 grid h-16 grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 border-b border-border bg-surface/80 px-4 backdrop-blur-xl sm:px-6">
        <Button className="lg:hidden" size="icon" variant="ghost" onClick={() => setMobileMenu(true)} aria-label="Abrir menú"><Menu className="size-5"/></Button>
        <div className="min-w-0"><h1 className="truncate text-base font-bold sm:text-lg">{title}</h1><p className="hidden truncate text-xs text-muted-foreground sm:block">Panel docente · Institución Educativa San Rafael</p></div>
        <div className="relative flex shrink-0 items-center gap-2"><Button size="icon" variant="secondary" aria-label="Notificaciones" onClick={() => setNoticeOpen(!noticeOpen)}><Bell className="size-4"/><span className="absolute right-0 top-0 size-2 rounded-full bg-warning"/></Button><div className="flex items-center gap-2 rounded-lg border border-border bg-surface p-1 pr-2"><UserAvatar user={user}/><span className="hidden max-w-40 truncate text-sm font-semibold sm:inline">{shortName(user)}</span>{isDemo(user) && <span className="rounded-full bg-warning-soft px-2 py-0.5 text-[10px] font-bold uppercase text-warning">Prueba</span>}</div>{noticeOpen && <div className="glass-panel absolute right-0 top-12 w-72 rounded-xl p-4"><p className="font-semibold">Notificaciones</p><p className="mt-3 rounded-lg bg-warning-soft p-3 text-xs text-muted-foreground">El curso de Fracciones tiene una observación de calidad pendiente.</p></div>}</div>
      </header>
      <main className="mx-auto max-w-6xl p-4 sm:p-6">{view === "dashboard" && <Dashboard go={go}/>} {view === "courses" && <Courses go={go}/>} {view === "generator" && <Generator onComplete={(t, c) => { setJob(t); setJobConfig(c); go("result"); }}/>} {view === "settings" && <SettingsView user={user}/>} {view === "result" && <Result go={go} job={job} config={jobConfig}/>}</main>
    </div>
  </div>;
}

function Dashboard({ go }: { go: (v: View) => void }) {
  const stats: Array<[string, string, string, LucideIcon]> = [["Cursos generados", "24", "+3 esta semana", BookOpen], ["Borradores activos", "6", "2 en revisión", FileText]];
  return <div className="space-y-5"><div className="grid gap-4 sm:grid-cols-2">{stats.map(([label,value,detail,Icon]) => <V2Mark key={label}><div className="glass-panel h-full rounded-xl p-5"><div className="flex items-start justify-between"><div><p className="text-xs font-semibold uppercase text-muted-foreground">{label}</p><p className="mt-2 text-3xl font-bold text-primary">{value}</p><p className="mt-1 text-xs text-muted-foreground">{detail}</p></div><span className="grid size-10 place-items-center rounded-lg bg-primary-soft text-primary"><Icon className="size-5"/></span></div></div></V2Mark>)}</div>
    <section className="glass-panel overflow-hidden rounded-xl"><div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 border-b border-border p-4 sm:p-5"><div className="min-w-0"><h2 className="font-bold">Cursos recientes</h2><p className="text-xs text-muted-foreground">Historial de cursos disponible en la versión 2.0.</p></div><Button size="sm" onClick={() => go("generator")}><Plus className="size-4"/><span className="hidden sm:inline">Generar curso</span></Button></div><V2Mark><CourseList/></V2Mark></section>
    <section className="rounded-xl border border-primary bg-primary p-5 text-primary-foreground shadow-lg"><Sparkles className="size-6"/><h2 className="mt-4 text-lg font-bold">Convierte una idea en una secuencia didáctica.</h2><p className="mt-2 text-sm text-primary-foreground/80">Define el tema, la audiencia y la metodología. SICCIA organiza el resto.</p><Button className="mt-5 bg-surface text-primary hover:bg-primary-soft" onClick={() => go("generator")}>Comenzar ahora<ChevronRight className="size-4"/></Button></section>
  </div>;
}

function CourseList() { return <div className="divide-y divide-border">{courses.map((c) => <div key={c.title} className="grid grid-cols-[auto_minmax(0,1fr)] gap-3 p-4 sm:grid-cols-[auto_minmax(0,1fr)_auto] sm:items-center sm:px-5"><span className="grid size-10 shrink-0 place-items-center rounded-lg bg-primary-soft text-xs font-bold text-primary">{c.initials}</span><div className="min-w-0"><p className="truncate text-sm font-semibold">{c.title}</p><p className="truncate text-xs text-muted-foreground">{c.meta}</p></div><div className="col-start-2 flex items-center gap-3 sm:col-auto"><div className="h-1.5 w-20 overflow-hidden rounded-full bg-muted"><div className={cn("h-full", c.tone === "success" ? "bg-success" : c.tone === "warning" ? "bg-warning" : "bg-primary")} style={{ width: `${c.progress}%` }}/></div><span className={cn("w-32 text-right text-xs font-semibold", c.tone === "success" ? "text-success" : c.tone === "warning" ? "text-warning" : "text-muted-foreground")}>{c.status}</span></div></div>)}</div> }

function Courses({ go }: { go: (v: View) => void }) { return <div className="space-y-4"><div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4"><div><h2 className="text-xl font-bold">Biblioteca de cursos</h2><p className="text-sm text-muted-foreground">La biblioteca estará disponible en la versión 2.0.</p></div><Button onClick={() => go("generator")}><Plus className="size-4"/>Nuevo</Button></div><V2Mark><section className="glass-panel overflow-hidden rounded-xl"><CourseList/></section></V2Mark></div>; }

type Activity = { tipo: string; cantidad: number; porcentaje: number | null };
const activityTypes = ["Examen", "Laboratorio", "Investigación", "Quiz"];
const questionTypeOptions = ["Selección múltiple", "Falso/verdadero", "Pregunta abierta", "Matching"];
const durationLabels: Record<string, string> = { corto: "4-6 horas", largo: "12-16 horas" };
const viaLabels: Record<string, string> = { programa: "Programa", contenido: "Contenido", evaluacion: "Evaluación", verificacion: "Verificación" };
const fileGroupLabels: Record<string, string> = { ...viaLabels, exportador: "Documentos PDF" };
const viaStatusLabels: Record<string, string> = { pendiente: "Pendiente", en_curso: "En curso", completada: "Completada", omitida: "Omitida" };
const isPdf = (nombre: string) => nombre.toLowerCase().endsWith(".pdf");
const formatSize = (bytes: number) => bytes >= 1024 * 1024 ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : `${(bytes / 1024).toFixed(1)} KB`;
const estadoLabels: Record<EstadoTrabajo, string> = { pendiente: "Pendiente", planificando: "Planificando", ejecutando: "Ejecutando", completado: "Generación completada", completado_con_errores: "Completado con errores", error: "Error" };
const POLL_MS = 1500;
const restrictions = ["Educación superior", "Formación profesional especializada", "Certificaciones", "Medicina clínica", "Gastronomía profesional", "Actividades peligrosas", "Asesoría profesional", "Persuasión política/religiosa", "Contenido sexual", "Actividades ilícitas", "Contenido no verificable"];

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return <button type="button" onClick={onClick} className={cn("rounded-lg border px-3 py-2 text-sm transition-colors", active ? "border-primary bg-primary-soft text-primary" : "border-border bg-surface hover:bg-muted")}>{active && <Check className="mr-1 inline size-3.5"/>}{children}</button>;
}
function Auto({ items }: { items: string[] }) {
  return <div className="flex flex-wrap gap-1.5">{items.map(i => <span key={i} className="rounded-full bg-muted px-2.5 py-1 text-xs text-muted-foreground"><Sparkles className="mr-1 inline size-3 text-primary"/>{i}</span>)}</div>;
}

function Generator({ onComplete }: { onComplete: (job: TrabajoRespuesta, config: Configurador) => void }) {
  const [step, setStep] = useState(1);
  const [tema, setTema] = useState("");
  const [duration, setDuration] = useState("");
  const [audience, setAudience] = useState("");
  const [method, setMethod] = useState("");
  const [closure, setClosure] = useState(true);
  const [examples, setExamples] = useState(true);
  const [workshops, setWorkshops] = useState(true);
  const images = false;
  const [mods, setMods] = useState<string[]>([]);
  const [newMod, setNewMod] = useState("");
  const [questionTypes, setQuestionTypes] = useState<string[]>([]);
  const [acts, setActs] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [job, setJob] = useState<TrabajoRespuesta | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const sentConfig = useRef<Configurador | null>(null);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;
  const durationOptions: Array<[string, string, string]> = [["corto","Curso corto","4–6 horas · tema puntual"],["largo","Curso largo","12–16 horas · unidad completa"]];
  useEffect(() => {
    if (!jobId) return;
    const ctrl = new AbortController();
    let timer: number | undefined;
    const tick = async () => {
      try {
        const t = await estadoCurso(jobId, ctrl.signal);
        setJob(t);
        if (!ESTADOS_FINALES.includes(t.estado)) { timer = window.setTimeout(tick, POLL_MS); return; }
        if (t.estado !== "error" && sentConfig.current) { const cfg = sentConfig.current; timer = window.setTimeout(() => onCompleteRef.current(t, cfg), 450); }
      } catch (e) {
        if (!ctrl.signal.aborted) setApiError(e instanceof Error ? e.message : "Error consultando el estado del trabajo.");
      }
    };
    void tick();
    return () => { ctrl.abort(); window.clearTimeout(timer); };
  }, [jobId]);
  const addMod = () => { if (newMod.trim() && mods.length < MAX_MODULOS) { setMods(m => [...m, newMod.trim()]); setNewMod(""); } };
  const removeMod = (i: number) => setMods(m => m.filter((_, j) => j !== i));
  const updAct = (i: number, patch: Partial<Activity>) => setActs(a => a.map((x, j) => j === i ? { ...x, ...patch } : x));
  const toggleQuestion = (q: string) => setQuestionTypes(qs => qs.includes(q) ? qs.filter(x => x !== q) : [...qs, q]);
  const config = construirConfigurador({
    tema, publico: audience, duracion: durationLabels[duration] ?? "", metodologia: method, modulos: mods,
    ejemplos: examples, talleres: workshops, cierre: closure, tiposPregunta: questionTypes, actividades: acts, imagenes: images,
  });
  const errors = validarConfigurador(config);
  const evalErrors = errors.filter(e => /porcentaje|actividad/i.test(e));
  const stepValid = [tema.trim().length >= MIN_TEMA, mods.length <= MAX_MODULOS, evalErrors.length === 0, errors.length === 0];
  const pctSum = acts.reduce((s, a) => s + (a.porcentaje ?? 0), 0);
  const generate = async () => {
    if (errors.length) return;
    sentConfig.current = config;
    setJob(null); setJobId(null); setApiError(null); setLoading(true);
    try { setJobId((await crearCurso(config)).id); }
    catch (e) { setApiError(e instanceof Error ? e.message : "No se pudo crear el trabajo."); }
  };
  const reset = () => { setLoading(false); setJobId(null); setJob(null); setApiError(null); };
  const viaKeys = job && Object.keys(job.vias).length ? Object.keys(job.vias) : Object.keys(viaLabels).filter(k => k !== "verificacion");
  const doneVias = viaKeys.filter(k => { const v = job?.vias[k]; return !!v && v !== "en_curso" && v !== "pendiente"; }).length;
  const progress = !job ? 5 : job.estado === "pendiente" ? 10 : job.estado === "planificando" ? 25 : job.estado === "ejecutando" ? 40 + Math.round((doneVias / viaKeys.length) * 55) : 100;
  const stepState = (key: string): "done" | "active" | "wait" | "fail" => {
    if (key === "plan") return !job || job.estado === "pendiente" ? "wait" : job.estado === "planificando" ? "active" : job.estado === "error" && !Object.keys(job.vias).length ? "fail" : "done";
    const v = job?.vias[key];
    return !v || v === "pendiente" || v === "omitida" ? "wait" : v === "en_curso" ? "active" : v === "completada" ? "done" : "fail";
  };
  const phases: Array<[string, string]> = [["plan", "Planificación del curso"], ...viaKeys.map(k => [k, `Vía ${viaLabels[k] ?? k}`] as [string, string])];
  const failed = apiError ?? (job?.estado === "error" ? job.error ?? "La generación falló." : null);
  if (loading) return <section className="glass-panel mx-auto max-w-2xl rounded-xl p-8 text-center sm:p-12">
    <span className={cn("mx-auto grid size-16 place-items-center rounded-full", failed ? "bg-warning-soft" : "bg-primary-soft")}>{failed ? <CircleAlert className="size-7 text-warning"/> : <Bot className="size-7 spin-slow text-primary"/>}</span>
    <h2 className="mt-6 text-xl font-bold">{failed ? "No se pudo generar el curso" : "Orquestando tu curso"}</h2>
    <p className="mt-2 text-sm text-muted-foreground">{failed ?? (job ? `Trabajo ${job.id.slice(0, 8)} · estado: ${estadoLabels[job.estado]}` : "Enviando configuración al backend...")}</p>
    {!failed && <><div className="mx-auto mt-7 h-2 max-w-md overflow-hidden rounded-full bg-muted"><div className="h-full bg-primary transition-all" style={{width:`${progress}%`}}/></div><p className="mt-3 text-sm font-semibold text-primary">{progress}%</p></>}
    <div className="mt-8 grid gap-2 text-left sm:grid-cols-2">{phases.map(([k, x]) => { const s = stepState(k); return <div key={k} className={cn("rounded-lg border p-3 text-xs", s === "done" ? "border-success/20 bg-success-soft text-success" : s === "active" ? "border-primary/30 bg-primary-soft text-primary pulse-soft" : s === "fail" ? "border-destructive/30 bg-warning-soft text-destructive" : "border-border bg-muted text-muted-foreground")}>{s === "done" && <Check className="mr-1 inline size-3"/>}{s === "fail" && <X className="mr-1 inline size-3"/>}{x}</div>; })}</div>
    {failed && <div className="mt-7 flex flex-wrap justify-center gap-2"><Button variant="secondary" onClick={reset}>Volver al configurador</Button><Button onClick={generate}>Reintentar</Button></div>}
  </section>;
  const titles = ["Programa del curso", "Módulos y temas", "Evaluaciones", "Revisión y envío"];
  const yesNo = (label: string, hint: string, value: boolean, set: (v: boolean) => void) => <div className="flex items-center justify-between gap-4 rounded-lg border border-border bg-surface p-4"><div><p className="text-sm font-semibold">{label}</p><p className="text-xs text-muted-foreground">{hint}</p></div><div className="flex gap-2"><Chip active={value} onClick={()=>set(true)}>Sí</Chip><Chip active={!value} onClick={()=>set(false)}>No</Chip></div></div>;
  return <div className="mx-auto max-w-4xl"><div className="mb-5 flex items-center justify-between gap-3"><div><h2 className="text-xl font-bold">Configurador GIA</h2><p className="text-sm text-muted-foreground">Basado en el modelo de curso SICCIA (Matriz 1) y la evaluación de IAs (Matriz 2).</p></div><span className="shrink-0 rounded-full bg-primary-soft px-3 py-1 text-xs font-semibold text-primary">Paso {step} de 4</span></div>
    <div className="mb-6 grid grid-cols-4 gap-2">{titles.map((t,n)=><div key={t}><div className={cn("h-1.5 rounded-full", n+1<=step ? "bg-primary" : "bg-muted")}/><p className={cn("mt-1.5 hidden text-xs sm:block", n+1===step ? "font-semibold text-primary" : "text-muted-foreground")}>{t}</p></div>)}</div>
    <section className="glass-panel rounded-xl p-5 sm:p-7">
      {step===1 && <div className="space-y-5"><div><h3 className="font-bold">Nivel 1 · Programa del curso</h3><p className="text-sm text-muted-foreground">Campos configurables del programa.</p></div>
        <Field label="Nombre del curso" type="text" value={tema} onChange={e=>setTema(e.target.value)} minLength={MIN_TEMA} placeholder="Ej.: Introducción a la programación"/>
        <p className="-mt-3 text-xs text-muted-foreground">Los campos que dejes vacíos los completa la IA.</p>
        {tema.length > 0 && tema.trim().length < MIN_TEMA && <p className="-mt-3 text-xs text-destructive">Mínimo {MIN_TEMA} caracteres.</p>}
        <label className="block"><span className="mb-1.5 block text-sm font-medium">Dirigido a / público objetivo <span className="font-normal text-muted-foreground">(opcional)</span></span><select value={audience} onChange={e=>setAudience(e.target.value)} className={cn("h-11 w-full rounded-lg border border-input bg-surface px-3 text-sm", !audience && "text-muted-foreground")}><option value="">Selecciona el público</option><option>Básica primaria · Grados 3.º a 5.º</option><option>Básica secundaria · Grados 6.º a 9.º</option><option>Media · Grados 10.º y 11.º</option><option>Tutores y formadores independientes</option></select></label>
        <div><span className="text-sm font-medium">Duración <span className="font-normal text-muted-foreground">(opcional)</span></span><div className="mt-2 grid gap-3 sm:grid-cols-2">{durationOptions.map(([id,t,d])=><button key={id} onClick={()=>setDuration(d => d===id ? "" : id)} className={cn("rounded-lg border p-4 text-left",duration===id?"border-primary bg-primary-soft":"border-border bg-surface hover:bg-muted")}><p className="text-sm font-semibold">{t}</p><p className="mt-1 text-xs text-muted-foreground">{d}</p></button>)}</div></div>
        <div><span className="text-sm font-medium">Metodología de aprendizaje <span className="font-normal text-muted-foreground">(opcional)</span></span><div className="mt-2 flex flex-wrap gap-2">{["Learning to do","Aprendizaje por proyectos","Resolución de problemas","Aula invertida"].map(x=><Chip key={x} active={method===x} onClick={()=>setMethod(m => m===x ? "" : x)}>{x}</Chip>)}</div></div>
        <div className="rounded-lg border border-border bg-muted/50 p-4"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Generado automáticamente por la IA</p><Auto items={["Descripción / introducción","Justificación","Objetivo general","Objetivos específicos (máx. 4)","Resultados de aprendizaje","Requisitos previos","Bibliografía y fuentes"]}/></div>
      </div>}
      {step===2 && <div className="space-y-5"><div><h3 className="font-bold">Niveles 2 y 3 · Módulos y temas</h3><p className="text-sm text-muted-foreground">Define la lista de módulos (máx. {MAX_MODULOS}); la IA genera los temas de cada uno. Sin módulos, la IA los diseña.</p></div>
        <div className="space-y-2">{mods.map((m,i)=><div key={i} className="flex items-center gap-3 rounded-lg border border-border bg-surface p-3"><span className="grid size-7 shrink-0 place-items-center rounded-md bg-primary-soft text-xs font-bold text-primary">{i+1}</span><input aria-label={`Módulo ${i+1}`} value={m} onChange={e=>setMods(ms=>ms.map((x,j)=>j===i?e.target.value:x))} className="min-w-0 flex-1 bg-transparent text-sm outline-none"/><button aria-label="Quitar módulo" onClick={()=>removeMod(i)} className="rounded p-1 text-muted-foreground hover:bg-muted"><X className="size-4"/></button></div>)}</div>
        {mods.length===0 && <p className="rounded-lg bg-primary-soft p-3 text-xs text-primary"><Sparkles className="mr-1 inline size-3"/>Modo automático: la IA definirá los módulos.</p>}
        <div className="flex gap-2"><input value={newMod} onChange={e=>setNewMod(e.target.value)} onKeyDown={e=>e.key==="Enter"&&addMod()} placeholder="Nombre del nuevo módulo" className="h-10 min-w-0 flex-1 rounded-lg border border-input bg-surface px-3 text-sm"/><Button variant="secondary" disabled={mods.length>=MAX_MODULOS} onClick={addMod}><Plus className="size-4"/>Agregar</Button></div>
        {yesNo("Cierre por módulo", "Genera un resumen al final de cada módulo.", closure, setClosure)}
        {yesNo("Ejemplos prácticos", "Incluye ejemplos en cada tema.", examples, setExamples)}
        {yesNo("Talleres de práctica", "Un taller sin nota por módulo.", workshops, setWorkshops)}
        <div aria-disabled="true" className="flex items-center justify-between gap-4 rounded-lg border border-dashed border-border bg-muted/40 p-4"><div><p className="text-sm font-semibold text-muted-foreground">Imágenes <span className="ml-2 rounded-full bg-primary-soft px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-primary">Versión 2.0</span></p><p className="text-xs text-muted-foreground">Generación de imágenes disponible en la versión 2.0.</p></div><div className="flex gap-2"><button type="button" disabled className="cursor-not-allowed rounded-lg border border-border bg-surface px-3 py-2 text-sm text-muted-foreground opacity-50">Sí</button><button type="button" disabled className="cursor-not-allowed rounded-lg border border-border bg-surface px-3 py-2 text-sm text-muted-foreground opacity-50">No</button></div></div>
        <div className="grid gap-3 sm:grid-cols-2"><div className="rounded-lg border border-border bg-muted/50 p-4"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Por cada módulo</p><Auto items={["Introducción","Objetivos","Temas",...(closure?["Resumen / cierre"]:[]),...(workshops?["Taller de práctica"]:[])]}/></div><div className="rounded-lg border border-border bg-muted/50 p-4"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Por cada tema</p><Auto items={["Explicación","Diapositivas",...(examples?["Ejemplo"]:[]),...(images?["Imagen"]:[])]}/></div></div>
      </div>}
      {step===3 && <div className="space-y-5"><div><h3 className="font-bold">Nivel 4 · Evaluaciones</h3><p className="text-sm text-muted-foreground">Define los tipos de pregunta y las actividades calificables con su peso en la nota final.</p></div>
        <div><p className="mb-1.5 text-xs font-medium text-muted-foreground">Tipos de pregunta</p><div className="flex flex-wrap gap-2">{questionTypeOptions.map(q=><Chip key={q} active={questionTypes.includes(q)} onClick={()=>toggleQuestion(q)}>{q}</Chip>)}</div></div>
        {acts.map((a,i)=><div key={i} className="rounded-lg border border-border bg-surface p-4"><div className="mb-3 flex items-center justify-between"><p className="text-sm font-bold">Actividad {i+1}</p><button aria-label="Quitar actividad" onClick={()=>setActs(x=>x.filter((_,j)=>j!==i))} className="rounded p-1 text-muted-foreground hover:bg-muted"><X className="size-4"/></button></div>
          <p className="mb-1.5 text-xs font-medium text-muted-foreground">Tipo</p><div className="flex flex-wrap gap-2">{activityTypes.map(t=><Chip key={t} active={a.tipo===t} onClick={()=>updAct(i,{tipo:t})}>{t}</Chip>)}</div>
          <div className="mt-4 grid gap-3 sm:max-w-sm">
            <label className="block"><span className="mb-1.5 block text-xs font-medium text-muted-foreground">Porcentaje de la nota (vacío = lo define la IA)</span><input type="number" min={0} max={100} value={a.porcentaje ?? ""} onChange={e=>updAct(i,{porcentaje: e.target.value === "" ? null : Number(e.target.value)})} className="h-10 w-full rounded-lg border border-input bg-surface px-3 text-sm"/></label>
          </div></div>)}
        <div className="flex flex-wrap items-center justify-between gap-3"><Button variant="secondary" onClick={()=>setActs(x=>[...x,{tipo:"Examen",cantidad:1,porcentaje:null}])}><Plus className="size-4"/>Agregar actividad</Button><span className={cn("text-xs font-semibold", evalErrors.length ? "text-destructive" : "text-muted-foreground")}>Suma: {pctSum}% · Total actividades: {config.evaluacion.total_actividades ?? 0}</span></div>
        {evalErrors.map(e=><p key={e} className="text-xs text-destructive">{e}</p>)}
        <div className="rounded-lg border border-border bg-muted/50 p-4"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Generado automáticamente</p><Auto items={["Preguntas y ejercicios","Retroalimentación"]}/></div>
      </div>}
      {step===4 && <div className="space-y-5"><div><h3 className="font-bold">Revisión y envío</h3><p className="text-sm text-muted-foreground">La asignación de modelos de IA para cada tarea la gestiona el orquestador del backend.</p></div>
        <V2Mark label="Versión 2.0"><div className="rounded-lg border border-info/20 bg-primary-soft p-4 text-sm text-muted-foreground"><p className="font-medium text-foreground"><ShieldCheck className="mr-2 inline size-4 text-primary"/>Filtro transversal de restricciones</p><div className="mt-3 flex flex-wrap gap-1.5">{restrictions.map(r=><span key={r} className="rounded-full bg-surface px-2.5 py-1 text-xs">{r}</span>)}</div></div></V2Mark>
        <details className="rounded-lg border border-border bg-surface p-4 text-sm"><summary className="cursor-pointer font-medium"><FileText className="mr-2 inline size-4 text-primary"/>Vista previa del JSON para el backend</summary><pre className="mt-3 max-h-80 overflow-auto rounded-md bg-muted p-3 text-xs">{JSON.stringify(config, null, 2)}</pre></details>
        {errors.map(e=><p key={e} className="text-xs text-destructive">{e}</p>)}
      </div>}
      <div className="mt-7 flex flex-wrap justify-between gap-2 border-t border-border pt-5"><Button variant="secondary" disabled={step===1} onClick={()=>setStep(s=>s-1)}>Anterior</Button>{step<4?<Button disabled={!stepValid[step-1]} onClick={()=>setStep(s=>s+1)}>Continuar<ChevronRight className="size-4"/></Button>:<Button disabled={!stepValid[3]} onClick={() => void generate()}><Sparkles className="size-4"/>Generar curso con IA</Button>}</div></section>
    <p className="mt-4 flex items-center gap-2 text-xs text-muted-foreground"><CircleAlert className="size-4"/>SICCIA no genera formación médica, técnica especializada o de alto riesgo.</p></div>;
}

function Result({ go, job, config }: { go: (v: View) => void; job: TrabajoRespuesta | null; config: Configurador | null }) {
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  if (!job || !config) return <section className="glass-panel mx-auto max-w-xl rounded-xl p-8 text-center"><p className="text-sm text-muted-foreground">No hay un curso generado en esta sesión.</p><Button className="mt-4" onClick={() => go("generator")}>Generar curso</Button></section>;
  const run = async (key: string, fn: () => Promise<void>) => { setBusy(key); setError(null); try { await fn(); } catch (e) { setError(e instanceof Error ? e.message : "Error al descargar"); } finally { setBusy(null); } };
  const pdfs = job.archivos.filter(a => isPdf(a.nombre));
  const mds = job.archivos.filter(a => !isPdf(a.nombre));
  const byVia = [{ via: "exportador", files: pdfs }, ...Object.keys(viaLabels).map(v => ({ via: v, files: mds.filter(a => a.via === v) }))];
  const otros = mds.filter(a => !(a.via in viaLabels));
  if (otros.length) byVia.push({ via: "otros", files: otros });
  const ok = job.estado === "completado";
  const c = config.contenido;
  return <div className="space-y-5">
    <section className="glass-panel rounded-xl p-5"><div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center"><div>
      <span className={cn("inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold", ok ? "bg-success-soft text-success" : "bg-warning-soft text-warning")}>{ok ? <Check className="size-3"/> : <CircleAlert className="size-3"/>}{estadoLabels[job.estado]}</span>
      <h2 className="mt-3 text-xl font-bold">{config.datos.tema}</h2>
      <p className="mt-1 text-sm text-muted-foreground">{[config.datos.duracion_estimada, c.modulos_modo === "manual" ? `${c.modulos.length} módulos` : "Módulos automáticos", config.datos.metodologia].filter(Boolean).join(" · ")}</p>
    </div><Button disabled={!pdfs.length || busy !== null} title={pdfs.length ? undefined : "No hay PDF para descargar"} onClick={() => run("zip", () => descargarZipPdf(job.id, pdfs.map(p => p.nombre)))}><Download className="size-4"/>{busy === "zip" ? "Descargando..." : `Descargar PDF (.zip)`}</Button></div>
    {error && <p className="mt-3 text-xs text-destructive">{error}</p>}</section>
    <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]">
      <section className="glass-panel overflow-hidden rounded-xl"><div className="border-b border-border p-5"><h3 className="font-bold">Materiales generados</h3><p className="text-sm text-muted-foreground">{pdfs.length} PDF · {mds.length} Markdown</p></div>{!pdfs.length && job.archivos.length > 0 && <div className="mx-5 mt-4 rounded-lg border border-warning/25 bg-warning-soft p-3 text-xs text-muted-foreground"><CircleAlert className="mr-1 inline size-3 text-warning"/>El servidor no generó PDF para este trabajo; solo hay archivos Markdown. Revisa el log del backend: la conversión a PDF requiere las librerías <b>markdown</b> y <b>weasyprint</b>.</div>}
        {byVia.filter(g => g.files.length).map(g => <div key={g.via} className="border-b border-border p-4 last:border-0"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">{fileGroupLabels[g.via] ?? "Otros"}</p><div className="space-y-2">{g.files.map(f => <div key={f.nombre} className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 rounded-lg border border-border bg-surface p-3"><span className="grid size-8 place-items-center rounded-md bg-primary-soft text-primary"><FileText className="size-4"/></span><div className="min-w-0"><p className="truncate text-sm">{f.nombre}</p><p className="text-xs text-muted-foreground">{isPdf(f.nombre) ? "PDF" : "Markdown"} · {formatSize(f.tamano_bytes)}</p></div><Button size="sm" variant="secondary" disabled={busy !== null} onClick={() => run(f.nombre, () => descargarArchivo(job.id, f.nombre))}><Download className="size-4"/><span className="hidden sm:inline">{busy === f.nombre ? "..." : "Descargar"}</span></Button></div>)}</div></div>)}
        {!job.archivos.length && <p className="p-5 text-sm text-muted-foreground">El trabajo no generó archivos.</p>}
      </section>
      <aside className="space-y-4">
        <section className="glass-panel rounded-xl p-5"><h3 className="font-bold">Vías de trabajo</h3><div className="mt-4 space-y-3 text-sm">{Object.entries(job.vias).map(([v, s]) => <div key={v} className="flex items-start justify-between gap-3"><span className="text-muted-foreground">{viaLabels[v] ?? v}</span><b className={cn("text-right", s === "completada" ? "text-success" : s === "omitida" || s === "pendiente" ? "text-muted-foreground" : s === "en_curso" ? "text-primary" : "text-destructive")}>{viaStatusLabels[s] ?? s}</b></div>)}</div><p className="mt-4 text-xs text-muted-foreground">Trabajo {job.id.slice(0, 8)} · {new Date(job.creado_en).toLocaleString("es-CO")}</p></section>
        {job.error && <section className="rounded-xl border border-warning/25 bg-warning-soft p-5"><CircleAlert className="size-5 text-warning"/><p className="mt-2 text-xs text-muted-foreground">{job.error}</p></section>}
        <Button className="w-full" variant="secondary" onClick={() => go("generator")}>Generar otro curso</Button>
        <Button className="w-full" variant="ghost" onClick={() => go("dashboard")}>Volver al panel</Button>
      </aside>
    </div>
  </div>;
}

function SettingsView({ user }: { user: Usuario }){const [saved,setSaved]=useState(false);return <section className="glass-panel mx-auto max-w-2xl rounded-xl p-5 sm:p-7"><h2 className="text-xl font-bold">Información personal</h2><p className="mt-1 text-sm text-muted-foreground">Datos del docente que se muestran en SICCIA.</p><div className="mt-6 space-y-5"><Field label="Nombre visible" defaultValue={displayName(user)}/>{user.email && <label className="block"><span className="mb-1.5 block text-sm font-medium">Correo electrónico</span><input readOnly value={user.email} className="h-11 w-full rounded-lg border border-input bg-muted px-3 text-sm text-muted-foreground"/></label>}<label className="block"><span className="mb-1.5 block text-sm font-medium">Institución</span><input className="h-11 w-full rounded-lg border border-input bg-surface px-3 text-sm" defaultValue="Institución Educativa San Rafael"/></label><Button onClick={()=>setSaved(true)}>{saved?<><Check className="size-4"/>Cambios guardados</>:"Guardar cambios"}</Button></div></section>}