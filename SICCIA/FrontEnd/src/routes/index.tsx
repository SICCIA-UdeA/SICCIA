import { createFileRoute } from "@tanstack/react-router";
import {
  Archive, Bell, BookOpen, Bot, Check, ChevronDown, ChevronRight, CircleAlert,
  ClipboardCheck, Download, File, FileSpreadsheet, FileText, GraduationCap, LayoutDashboard,
  LogOut, Menu, Plus, Settings, ShieldCheck, Sparkles, User, X, Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import type { LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

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

type View = "dashboard" | "courses" | "generator" | "quality" | "settings" | "result";
type AuthMode = "login" | "register" | "forgot";

const courses = [
  { initials: "JV", title: "Lenguaje de programación Java", meta: "Secundaria · 16 h · Learning to do", status: "Generado", tone: "success", progress: 100 },
  { initials: "FR", title: "Fracciones para Básica Primaria", meta: "Primaria · 6 h · Resolución de problemas", status: "En revisión de calidad", tone: "warning", progress: 72 },
  { initials: "EA", title: "Ecosistemas andinos y biodiversidad", meta: "Primaria · 4 h · Aprendizaje por proyectos", status: "Pendiente de aprobación", tone: "muted", progress: 38 },
];

const modules: Array<{ title: string; duration: string; files: Array<[string, string]> }> = [
  { title: "Módulo 1 · Fundamentos y contexto", duration: "2 h", files: [["Programa del módulo", "DOC"], ["Presentación introductoria", "PPT"], ["Cuestionario diagnóstico", "TXT"]] },
  { title: "Módulo 2 · Conceptos esenciales", duration: "2 h", files: [["Guía conceptual", "DOC"], ["Laboratorio práctico", "DOC"], ["Registro de resultados", "XLS"]] },
  { title: "Módulo 3 · Aplicación y cierre", duration: "2 h", files: [["Presentación de cierre", "PPT"], ["Cuestionario final", "TXT"], ["Rúbrica de evaluación", "XLS"]] },
];

function Logo() {
  return <div className="flex items-center gap-2"><span className="grid size-9 place-items-center rounded-lg bg-primary text-sm font-bold text-primary-foreground shadow-sm">S</span><span className="font-bold text-foreground">SICCIA</span></div>;
}

function Index() {
  const [authenticated, setAuthenticated] = useState(false);
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [view, setView] = useState<View>("dashboard");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [noticeOpen, setNoticeOpen] = useState(false);
  if (!authenticated) return <AuthScreen mode={authMode} setMode={setAuthMode} onAccess={() => setAuthenticated(true)} />;
  return <AppShell view={view} setView={setView} mobileMenu={mobileMenu} setMobileMenu={setMobileMenu} collapsed={collapsed} setCollapsed={setCollapsed} noticeOpen={noticeOpen} setNoticeOpen={setNoticeOpen} onLogout={() => { setAuthenticated(false); setView("dashboard"); }} />;
}

function AuthScreen({ mode, setMode, onAccess }: { mode: AuthMode; setMode: (m: AuthMode) => void; onAccess: () => void }) {
  const [sent, setSent] = useState(false);
  const title = mode === "login" ? "Bienvenido de nuevo" : mode === "register" ? "Crea tu cuenta docente" : "Recupera tu acceso";
  return <main className="relative grid min-h-screen place-items-center overflow-hidden bg-background px-4 py-10">
    <div className="absolute inset-x-0 top-0 h-1 bg-primary" />
    <div className="absolute left-[8%] top-[10%] size-72 rounded-full bg-primary-soft/70 blur-3xl" />
    <section className="glass-panel relative z-10 w-full max-w-md rounded-2xl p-6 sm:p-8">
      <div className="mb-8 flex justify-center"><Logo /></div>
      <div className="text-center"><h1 className="text-2xl font-bold">{title}</h1><p className="mt-2 text-sm text-muted-foreground">{mode === "forgot" ? "Te enviaremos instrucciones para restablecer tu contraseña." : "Tu espacio para diseñar cursos con IA y criterio pedagógico."}</p></div>
      {sent ? <div className="mt-8 rounded-xl border border-success/20 bg-success-soft p-5 text-center"><Check className="mx-auto size-7 text-success"/><p className="mt-2 font-semibold">Revisa tu correo</p><p className="mt-1 text-sm text-muted-foreground">Enviamos un enlace de recuperación de demostración.</p><Button className="mt-4" variant="secondary" onClick={() => { setSent(false); setMode("login"); }}>Volver al acceso</Button></div> :
      <form className="mt-7 space-y-4" onSubmit={(e) => { e.preventDefault(); mode === "forgot" ? setSent(true) : onAccess(); }}>
        {mode === "register" && <Field label="Nombre completo" type="text" placeholder="María González" />}
        <Field label="Correo electrónico" type="email" placeholder="docente@institucion.edu.co" />
        {mode !== "forgot" && <Field label="Contraseña" type="password" placeholder="••••••••" />}
        {mode === "login" && <div className="text-right"><button type="button" className="text-xs font-semibold text-primary hover:underline" onClick={() => setMode("forgot")}>¿Olvidaste tu contraseña?</button></div>}
        <Button className="w-full" type="submit">{mode === "login" ? "Ingresar a SICCIA" : mode === "register" ? "Crear cuenta" : "Enviar instrucciones"}<ChevronRight className="size-4"/></Button>
        {mode !== "forgot" && <div className="pt-1">
          <div className="flex items-center gap-3"><span className="h-px flex-1 bg-border"/><span className="text-xs text-muted-foreground">o continúa con</span><span className="h-px flex-1 bg-border"/></div>
          <Button type="button" variant="secondary" className="mt-3 w-full" onClick={onAccess}><GoogleMark className="size-4"/>Continuar con Google</Button>
        </div>}
      </form>}
      {!sent && mode !== "forgot" && <p className="mt-6 text-center text-sm text-muted-foreground">{mode === "login" ? "¿Eres nuevo en SICCIA?" : "¿Ya tienes una cuenta?"} <button className="font-semibold text-primary hover:underline" onClick={() => setMode(mode === "login" ? "register" : "login")}>{mode === "login" ? "Regístrate" : "Ingresa"}</button></p>}
      <p className="mt-7 text-center text-xs text-muted-foreground">Prototipo académico · Los accesos son simulados</p>
    </section>
  </main>;
}

function GoogleMark({ className }: { className?: string }) {
  return <svg className={className} viewBox="0 0 24 24" aria-hidden="true"><path fill="#4285F4" d="M23.5 12.27c0-.85-.08-1.66-.22-2.45H12v4.64h6.45a5.52 5.52 0 0 1-2.39 3.62v3h3.87c2.26-2.09 3.57-5.16 3.57-8.81Z"/><path fill="#34A853" d="M12 24c3.24 0 5.96-1.07 7.94-2.91l-3.87-3c-1.08.72-2.45 1.15-4.07 1.15-3.13 0-5.78-2.11-6.73-4.96H1.29v3.1A12 12 0 0 0 12 24Z"/><path fill="#FBBC05" d="M5.27 14.28a7.2 7.2 0 0 1 0-4.56v-3.1H1.29a12 12 0 0 0 0 10.76l3.98-3.1Z"/><path fill="#EA4335" d="M12 4.76c1.76 0 3.34.6 4.58 1.79l3.44-3.44A11.98 11.98 0 0 0 12 0 12 12 0 0 0 1.29 6.62l3.98 3.1C6.22 6.87 8.87 4.76 12 4.76Z"/></svg>;
}

function Field({ label, ...props }: { label: string } & React.InputHTMLAttributes<HTMLInputElement>) {
  return <label className="block"><span className="mb-1.5 block text-sm font-medium">{label}</span><input className="h-11 w-full rounded-lg border border-input bg-surface px-3 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/15" required {...props}/></label>;
}

const nav = [
  ["dashboard", "Panel principal", LayoutDashboard], ["courses", "Mis cursos", BookOpen], ["generator", "Generar nuevo curso", Sparkles], ["quality", "Historial de calidad", ClipboardCheck], ["settings", "Configuración", Settings],
] as const;

function AppShell(props: { view: View; setView: (v: View) => void; mobileMenu: boolean; setMobileMenu: (v: boolean) => void; collapsed: boolean; setCollapsed: (v: boolean) => void; noticeOpen: boolean; setNoticeOpen: (v: boolean) => void; onLogout: () => void }) {
  const { view, setView, mobileMenu, setMobileMenu, collapsed, setCollapsed, noticeOpen, setNoticeOpen, onLogout } = props;
  const title = ({ dashboard: "Panel principal", courses: "Mis cursos", generator: "Generar nuevo curso", quality: "Evaluaciones de calidad", settings: "Configuración", result: "Curso generado" } as const)[view];
  const go = (v: View) => { setView(v); setMobileMenu(false); };
  return <div className="min-h-screen bg-background text-foreground">
    {mobileMenu && <button aria-label="Cerrar menú" className="fixed inset-0 z-30 bg-foreground/20 lg:hidden" onClick={() => setMobileMenu(false)} />}
    <aside className={cn("fixed inset-y-0 left-0 z-40 flex flex-col border-r border-border bg-surface/95 p-3 backdrop-blur-xl transition-[width,transform] lg:translate-x-0", mobileMenu ? "translate-x-0" : "-translate-x-full", collapsed ? "w-20" : "w-64")}>
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center px-2 py-2"><div className={cn("min-w-0 overflow-hidden", collapsed && "lg:w-9")}><Logo /></div><Button className="lg:hidden" size="icon" variant="ghost" onClick={() => setMobileMenu(false)} aria-label="Cerrar menú"><X className="size-5"/></Button></div>
      <nav className="mt-5 space-y-1">{nav.map(([id, label, Icon]) => <button key={id} onClick={() => go(id)} title={label} className={cn("flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors", view === id ? "bg-primary-soft text-primary" : "text-muted-foreground hover:bg-muted hover:text-foreground", collapsed && "lg:justify-center lg:px-0")}><Icon className="size-4 shrink-0"/><span className={cn("truncate", collapsed && "lg:hidden")}>{label}</span></button>)}</nav>
      <div className={cn("mt-auto rounded-xl border border-border bg-primary-soft p-3", collapsed && "lg:p-2")}><Zap className="size-4 text-primary"/><div className={cn(collapsed && "lg:hidden")}><p className="mt-2 text-xs font-medium text-muted-foreground">Créditos IA</p><p className="text-lg font-bold text-primary">48 <span className="text-xs font-normal text-muted-foreground">/ 60</span></p><div className="mt-2 h-1.5 overflow-hidden rounded-full bg-surface"><div className="h-full w-4/5 bg-primary"/></div></div></div>
      <Button className="mt-3 w-full" variant="ghost" onClick={onLogout}><LogOut className="size-4"/><span className={cn(collapsed && "lg:hidden")}>Cerrar sesión</span></Button>
      <Button className="absolute -right-4 top-20 hidden rounded-full bg-surface shadow-sm lg:inline-flex" size="icon" variant="secondary" onClick={() => setCollapsed(!collapsed)} aria-label={collapsed ? "Expandir menú" : "Contraer menú"}><ChevronRight className={cn("size-4 transition-transform", !collapsed && "rotate-180")}/></Button>
    </aside>
    <div className={cn("transition-[margin]", collapsed ? "lg:ml-20" : "lg:ml-64")}>
      <header className="sticky top-0 z-20 grid h-16 grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 border-b border-border bg-surface/80 px-4 backdrop-blur-xl sm:px-6">
        <Button className="lg:hidden" size="icon" variant="ghost" onClick={() => setMobileMenu(true)} aria-label="Abrir menú"><Menu className="size-5"/></Button>
        <div className="min-w-0"><h1 className="truncate text-base font-bold sm:text-lg">{title}</h1><p className="hidden truncate text-xs text-muted-foreground sm:block">Panel docente · Institución Educativa San Rafael</p></div>
        <div className="relative flex shrink-0 items-center gap-2"><Button size="icon" variant="secondary" aria-label="Notificaciones" onClick={() => setNoticeOpen(!noticeOpen)}><Bell className="size-4"/><span className="absolute right-0 top-0 size-2 rounded-full bg-warning"/></Button><div className="flex items-center gap-2 rounded-lg border border-border bg-surface p-1 pr-2"><span className="grid size-8 place-items-center rounded-md bg-primary-soft text-xs font-bold text-primary">MG</span><span className="hidden text-sm font-semibold sm:inline">Marcela G.</span></div>{noticeOpen && <div className="glass-panel absolute right-0 top-12 w-72 rounded-xl p-4"><p className="font-semibold">Notificaciones</p><p className="mt-3 rounded-lg bg-warning-soft p-3 text-xs text-muted-foreground">El curso de Fracciones tiene una observación de calidad pendiente.</p></div>}</div>
      </header>
      <main className="mx-auto max-w-6xl p-4 sm:p-6">{view === "dashboard" && <Dashboard go={go}/>} {view === "courses" && <Courses go={go}/>} {view === "generator" && <Generator onComplete={() => go("result")}/>} {view === "quality" && <Quality/>} {view === "settings" && <SettingsView/>} {view === "result" && <Result go={go}/>}</main>
    </div>
  </div>;
}

function Dashboard({ go }: { go: (v: View) => void }) {
  const stats: Array<[string, string, string, LucideIcon]> = [["Cursos generados", "24", "+3 esta semana", BookOpen], ["Borradores activos", "6", "2 en revisión", FileText], ["Créditos disponibles", "48", "de 60 mensuales", Zap]];
  return <div className="space-y-5"><div className="grid gap-4 sm:grid-cols-3">{stats.map(([label,value,detail,Icon]) => <div key={label} className="glass-panel rounded-xl p-5"><div className="flex items-start justify-between"><div><p className="text-xs font-semibold uppercase text-muted-foreground">{label}</p><p className="mt-2 text-3xl font-bold text-primary">{value}</p><p className="mt-1 text-xs text-muted-foreground">{detail}</p></div><span className="grid size-10 place-items-center rounded-lg bg-primary-soft text-primary"><Icon className="size-5"/></span></div></div>)}</div>
    <section className="glass-panel overflow-hidden rounded-xl"><div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 border-b border-border p-4 sm:p-5"><div className="min-w-0"><h2 className="font-bold">Cursos recientes</h2><p className="text-xs text-muted-foreground">Continúa donde terminaste o revisa el estado.</p></div><Button size="sm" onClick={() => go("generator")}><Plus className="size-4"/><span className="hidden sm:inline">Generar curso</span></Button></div><CourseList/></section>
    <div className="grid gap-4 md:grid-cols-2"><section className="glass-panel rounded-xl p-5"><div className="flex items-center justify-between"><h2 className="font-bold">Calidad más reciente</h2><span className="text-xs text-muted-foreground">Fracciones · Módulo 2</span></div><div className="mt-4 flex items-center gap-4"><span className="grid size-16 shrink-0 place-items-center rounded-full border-4 border-success/25 text-xl font-bold text-success">94%</span><div><p className="text-sm font-semibold">Veracidad frente a fuentes oficiales</p><p className="mt-1 text-xs text-muted-foreground">1 inconsistencia requiere revisión docente.</p></div></div><Button className="mt-4" variant="secondary" size="sm" onClick={() => go("quality")}>Ver informe completo</Button></section><section className="rounded-xl border border-primary bg-primary p-5 text-primary-foreground shadow-lg"><Sparkles className="size-6"/><h2 className="mt-4 text-lg font-bold">Convierte una idea en una secuencia didáctica.</h2><p className="mt-2 text-sm text-primary-foreground/80">Define el tema, la audiencia y la metodología. SICCIA organiza el resto.</p><Button className="mt-5 bg-surface text-primary hover:bg-primary-soft" onClick={() => go("generator")}>Comenzar ahora<ChevronRight className="size-4"/></Button></section></div>
  </div>;
}

function CourseList() { return <div className="divide-y divide-border">{courses.map((c) => <div key={c.title} className="grid grid-cols-[auto_minmax(0,1fr)] gap-3 p-4 sm:grid-cols-[auto_minmax(0,1fr)_auto] sm:items-center sm:px-5"><span className="grid size-10 shrink-0 place-items-center rounded-lg bg-primary-soft text-xs font-bold text-primary">{c.initials}</span><div className="min-w-0"><p className="truncate text-sm font-semibold">{c.title}</p><p className="truncate text-xs text-muted-foreground">{c.meta}</p></div><div className="col-start-2 flex items-center gap-3 sm:col-auto"><div className="h-1.5 w-20 overflow-hidden rounded-full bg-muted"><div className={cn("h-full", c.tone === "success" ? "bg-success" : c.tone === "warning" ? "bg-warning" : "bg-primary")} style={{ width: `${c.progress}%` }}/></div><span className={cn("w-32 text-right text-xs font-semibold", c.tone === "success" ? "text-success" : c.tone === "warning" ? "text-warning" : "text-muted-foreground")}>{c.status}</span></div></div>)}</div> }

function Courses({ go }: { go: (v: View) => void }) { return <div className="space-y-4"><div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4"><div><h2 className="text-xl font-bold">Biblioteca de cursos</h2><p className="text-sm text-muted-foreground">24 cursos y 6 borradores.</p></div><Button onClick={() => go("generator")}><Plus className="size-4"/>Nuevo</Button></div><section className="glass-panel overflow-hidden rounded-xl"><CourseList/></section></div>; }

type Evaluation = { type: string; scope: number[] };
const evalTypes = ["Selección múltiple", "Preguntas abiertas", "Taller", "Examen", "Matching"];
const aiTasks: Array<{ task: string; options: Array<{ name: string; note: string; halluc: string; cost: string }> }> = [
  { task: "Programa del curso", options: [
    { name: "ChatGPT", note: "Prompt simple, texto plano", halluc: "No reportada", cost: "Segundos" },
    { name: "Claude", note: "Prompt simple, texto plano", halluc: "No reportada", cost: "~2.5 min" },
    { name: "Gemini", note: "Requiere indicar “solo texto”", halluc: "No reportada", cost: "~1 min" },
    { name: "Grok", note: "Prompt simple, texto plano", halluc: "No reportada", cost: "~2 min" } ] },
  { task: "Material de lectura y evaluación", options: [
    { name: "Claude", note: "Única que citó fuentes reales", halluc: "Baja", cost: "~2.5 min" },
    { name: "ChatGPT", note: "Correcto pero sin fuentes", halluc: "Media", cost: "Rápido" },
    { name: "Gemini", note: "Mejor nivel cognitivo", halluc: "Media", cost: "Rápido" } ] },
  { task: "Enlaces a recursos complementarios", options: [
    { name: "ChatGPT", note: "Enlaces funcionales", halluc: "Baja", cost: "Rápido" },
    { name: "Grok", note: "Variados, multi-idioma", halluc: "Baja", cost: "~2 min" },
    { name: "Claude", note: "Pocas fallas", halluc: "Baja", cost: "+4 min" },
    { name: "Perplexity", note: "Requiere revisión manual", halluc: "Media", cost: "Rápido" } ] },
  { task: "Verificación de veracidad", options: [
    { name: "Consensus", note: "La más rigurosa", halluc: "Muy baja", cost: "Rápido" },
    { name: "ScholarAI", note: "Fuentes reales", halluc: "Baja", cost: "Créditos Pro" },
    { name: "Elicit", note: "Detecta matices", halluc: "Baja", cost: "Lento" },
    { name: "NotebookLM", note: "Solo coherencia interna", halluc: "—", cost: "Rápido" } ] },
];
const restrictions = ["Educación superior", "Formación profesional especializada", "Certificaciones", "Medicina clínica", "Gastronomía profesional", "Actividades peligrosas", "Asesoría profesional", "Persuasión política/religiosa", "Contenido sexual", "Actividades ilícitas", "Contenido no verificable"];

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return <button type="button" onClick={onClick} className={cn("rounded-lg border px-3 py-2 text-sm transition-colors", active ? "border-primary bg-primary-soft text-primary" : "border-border bg-surface hover:bg-muted")}>{active && <Check className="mr-1 inline size-3.5"/>}{children}</button>;
}
function Auto({ items }: { items: string[] }) {
  return <div className="flex flex-wrap gap-1.5">{items.map(i => <span key={i} className="rounded-full bg-muted px-2.5 py-1 text-xs text-muted-foreground"><Sparkles className="mr-1 inline size-3 text-primary"/>{i}</span>)}</div>;
}

function Generator({ onComplete }: { onComplete: () => void }) {
  const [step, setStep] = useState(1);
  const [duration, setDuration] = useState("corto");
  const [audience, setAudience] = useState("Básica primaria · Grados 3.º a 5.º");
  const [method, setMethod] = useState("Learning to do");
  const [closure, setClosure] = useState(true);
  const [mods, setMods] = useState(["¿Qué es una fracción?", "Fracciones equivalentes", "Operaciones con fracciones"]);
  const [newMod, setNewMod] = useState("");
  const [evals, setEvals] = useState<Evaluation[]>([{ type: "Selección múltiple", scope: [0, 1] }, { type: "Taller", scope: [2] }]);
  const [ai, setAi] = useState<string[]>(aiTasks.map(t => t.options[0]?.name ?? ""));
  const [loading, setLoading] = useState(false); const [progress, setProgress] = useState(0);
  const durationOptions: Array<[string, string, string]> = [["corto","Curso corto","4–6 horas · tema puntual"],["largo","Curso largo","12–16 horas · unidad completa"]];
  useEffect(() => { if (!loading) return; const timer = window.setInterval(() => setProgress(p => { if (p >= 100) { window.clearInterval(timer); window.setTimeout(onComplete, 450); return 100; } return p + 5; }), 220); return () => window.clearInterval(timer); }, [loading, onComplete]);
  const addMod = () => { if (newMod.trim()) { setMods(m => [...m, newMod.trim()]); setNewMod(""); } };
  const removeMod = (i: number) => { setMods(m => m.filter((_, j) => j !== i)); setEvals(e => e.map(ev => ({ ...ev, scope: ev.scope.filter(s => s !== i).map(s => s > i ? s - 1 : s) }))); };
  const updEval = (i: number, patch: Partial<Evaluation>) => setEvals(e => e.map((ev, j) => j === i ? { ...ev, ...patch } : ev));
  const valid = mods.length > 0 && evals.every(e => e.scope.length > 0);
  const phases = ["Filtro de restricciones", "Nivel 1 · Programa", "Nivel 2 · Módulos", "Nivel 3 · Temas", "Nivel 4 · Evaluaciones", "Verificación de veracidad"];
  const phase = Math.min(phases.length - 1, Math.floor(progress / (100 / phases.length)));
  if (loading) return <section className="glass-panel mx-auto max-w-2xl rounded-xl p-8 text-center sm:p-12"><span className="mx-auto grid size-16 place-items-center rounded-full bg-primary-soft"><Bot className="size-7 spin-slow text-primary"/></span><h2 className="mt-6 text-xl font-bold">Orquestando tu curso</h2><p className="mt-2 text-sm text-muted-foreground">Cada IA trabaja en la tarea donde mostró mejores resultados.</p><div className="mx-auto mt-7 h-2 max-w-md overflow-hidden rounded-full bg-muted"><div className="h-full bg-primary transition-all" style={{width:`${progress}%`}}/></div><p className="mt-3 text-sm font-semibold text-primary">{progress}% · {phases[phase]}</p><div className="mt-8 grid gap-2 text-left sm:grid-cols-2">{phases.map((x,i)=><div key={x} className={cn("rounded-lg border p-3 text-xs", i < phase || progress>=100 ? "border-success/20 bg-success-soft text-success" : i===phase ? "border-primary/30 bg-primary-soft text-primary pulse-soft" : "border-border bg-muted text-muted-foreground")}>{(i < phase || progress>=100) && <Check className="mr-1 inline size-3"/>}{x}{i>=1&&i<=4 ? "" : ""}</div>)}</div></section>;
  const titles = ["Programa del curso", "Módulos y temas", "Evaluaciones", "Orquestación de IA"];
  return <div className="mx-auto max-w-4xl"><div className="mb-5 flex items-center justify-between gap-3"><div><h2 className="text-xl font-bold">Configurador GIA</h2><p className="text-sm text-muted-foreground">Basado en el modelo de curso SICCIA (Matriz 1) y la evaluación de IAs (Matriz 2).</p></div><span className="shrink-0 rounded-full bg-primary-soft px-3 py-1 text-xs font-semibold text-primary">Paso {step} de 4</span></div>
    <div className="mb-6 grid grid-cols-4 gap-2">{titles.map((t,n)=><div key={t}><div className={cn("h-1.5 rounded-full", n+1<=step ? "bg-primary" : "bg-muted")}/><p className={cn("mt-1.5 hidden text-xs sm:block", n+1===step ? "font-semibold text-primary" : "text-muted-foreground")}>{t}</p></div>)}</div>
    <section className="glass-panel rounded-xl p-5 sm:p-7">
      {step===1 && <div className="space-y-5"><div><h3 className="font-bold">Nivel 1 · Programa del curso</h3><p className="text-sm text-muted-foreground">Campos configurables del programa.</p></div>
        <Field label="Nombre del curso" type="text" defaultValue="Fracciones para Básica Primaria"/>
        <label className="block"><span className="mb-1.5 block text-sm font-medium">Dirigido a / público objetivo</span><select value={audience} onChange={e=>setAudience(e.target.value)} className="h-11 w-full rounded-lg border border-input bg-surface px-3 text-sm"><option>Básica primaria · Grados 3.º a 5.º</option><option>Básica secundaria · Grados 6.º a 9.º</option><option>Media · Grados 10.º y 11.º</option><option>Tutores y formadores independientes</option></select></label>
        <div><span className="text-sm font-medium">Duración</span><div className="mt-2 grid gap-3 sm:grid-cols-2">{durationOptions.map(([id,t,d])=><button key={id} onClick={()=>setDuration(id)} className={cn("rounded-lg border p-4 text-left",duration===id?"border-primary bg-primary-soft":"border-border bg-surface hover:bg-muted")}><p className="text-sm font-semibold">{t}</p><p className="mt-1 text-xs text-muted-foreground">{d}</p></button>)}</div></div>
        <div><span className="text-sm font-medium">Metodología de aprendizaje</span><div className="mt-2 flex flex-wrap gap-2">{["Learning to do","Aprendizaje por proyectos","Resolución de problemas","Aula invertida"].map(x=><Chip key={x} active={method===x} onClick={()=>setMethod(x)}>{x}</Chip>)}</div></div>
        <div className="rounded-lg border border-border bg-muted/50 p-4"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Generado automáticamente por la IA</p><Auto items={["Descripción / introducción","Justificación","Objetivo general","Objetivos específicos (máx. 4)","Resultados de aprendizaje","Requisitos previos","Bibliografía y fuentes"]}/></div>
      </div>}
      {step===2 && <div className="space-y-5"><div><h3 className="font-bold">Niveles 2 y 3 · Módulos y temas</h3><p className="text-sm text-muted-foreground">Define la lista de módulos; la IA genera los temas de cada uno.</p></div>
        <div className="space-y-2">{mods.map((m,i)=><div key={i} className="flex items-center gap-3 rounded-lg border border-border bg-surface p-3"><span className="grid size-7 shrink-0 place-items-center rounded-md bg-primary-soft text-xs font-bold text-primary">{i+1}</span><input aria-label={`Módulo ${i+1}`} value={m} onChange={e=>setMods(ms=>ms.map((x,j)=>j===i?e.target.value:x))} className="min-w-0 flex-1 bg-transparent text-sm outline-none"/><button aria-label="Quitar módulo" onClick={()=>removeMod(i)} className="rounded p-1 text-muted-foreground hover:bg-muted"><X className="size-4"/></button></div>)}</div>
        <div className="flex gap-2"><input value={newMod} onChange={e=>setNewMod(e.target.value)} onKeyDown={e=>e.key==="Enter"&&addMod()} placeholder="Nombre del nuevo módulo" className="h-10 min-w-0 flex-1 rounded-lg border border-input bg-surface px-3 text-sm"/><Button variant="secondary" onClick={addMod}><Plus className="size-4"/>Agregar</Button></div>
        <div className="flex items-center justify-between gap-4 rounded-lg border border-border bg-surface p-4"><div><p className="text-sm font-semibold">Cierre por módulo</p><p className="text-xs text-muted-foreground">Genera un resumen al final de cada módulo.</p></div><div className="flex gap-2"><Chip active={closure} onClick={()=>setClosure(true)}>Sí</Chip><Chip active={!closure} onClick={()=>setClosure(false)}>No</Chip></div></div>
        <div className="grid gap-3 sm:grid-cols-2"><div className="rounded-lg border border-border bg-muted/50 p-4"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Por cada módulo</p><Auto items={["Introducción","Objetivos","Temas",...(closure?["Resumen / cierre"]:[]),"Recursos complementarios"]}/></div><div className="rounded-lg border border-border bg-muted/50 p-4"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Por cada tema</p><Auto items={["Explicación","Diapositivas","Ejemplo","Enlaces (video, web)","Actividad formativa (sin nota)"]}/><p className="mt-2 text-xs text-warning"><CircleAlert className="mr-1 inline size-3"/>Imagen del tema: experimental (riesgo de alucinación)</p></div></div>
      </div>}
      {step===3 && <div className="space-y-5"><div><h3 className="font-bold">Nivel 4 · Evaluaciones</h3><p className="text-sm text-muted-foreground">Independientes de los módulos: tú decides cuántas, de qué tipo y qué cubre cada una.</p></div>
        {evals.map((ev,i)=><div key={i} className="rounded-lg border border-border bg-surface p-4"><div className="mb-3 flex items-center justify-between"><p className="text-sm font-bold">Evaluación {i+1}</p>{evals.length>1&&<button aria-label="Quitar evaluación" onClick={()=>setEvals(e=>e.filter((_,j)=>j!==i))} className="rounded p-1 text-muted-foreground hover:bg-muted"><X className="size-4"/></button>}</div>
          <p className="mb-1.5 text-xs font-medium text-muted-foreground">Tipo</p><div className="flex flex-wrap gap-2">{evalTypes.map(t=><Chip key={t} active={ev.type===t} onClick={()=>updEval(i,{type:t})}>{t}</Chip>)}</div>
          <p className="mb-1.5 mt-4 text-xs font-medium text-muted-foreground">Alcance (módulos que cubre)</p><div className="flex flex-wrap gap-2">{mods.map((m,j)=><Chip key={j} active={ev.scope.includes(j)} onClick={()=>updEval(i,{scope: ev.scope.includes(j)?ev.scope.filter(s=>s!==j):[...ev.scope,j].sort()})}>M{j+1} · {m}</Chip>)}</div>
          {ev.scope.length===0&&<p className="mt-2 text-xs text-destructive">Selecciona al menos un módulo.</p>}</div>)}
        <Button variant="secondary" onClick={()=>setEvals(e=>[...e,{type:"Selección múltiple",scope:[]}])}><Plus className="size-4"/>Agregar evaluación</Button>
        <div className="rounded-lg border border-border bg-muted/50 p-4"><p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Generado automáticamente</p><Auto items={["Preguntas y ejercicios","Retroalimentación"]}/></div>
      </div>}
      {step===4 && <div className="space-y-5"><div><h3 className="font-bold">Orquestación de IA por tarea</h3><p className="text-sm text-muted-foreground">Recomendación según la evaluación de alucinación y costo (Matriz 2).</p></div>
        {aiTasks.map((t,i)=><div key={t.task}><p className="mb-2 text-sm font-semibold">Tarea {i+1} · {t.task}</p><div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">{t.options.map((o,k)=>{const on=ai[i]===o.name; return <button key={o.name} onClick={()=>setAi(a=>a.map((x,j)=>j===i?o.name:x))} className={cn("rounded-lg border p-3 text-left transition-colors",on?"border-primary bg-primary-soft":"border-border bg-surface hover:bg-muted")}><div className="flex items-center justify-between"><span className="text-sm font-bold">{o.name}</span>{k===0&&<span className="rounded-full bg-success-soft px-2 py-0.5 text-[10px] font-semibold text-success">Recomendada</span>}</div><p className="mt-1 text-xs text-muted-foreground">{o.note}</p><p className="mt-2 text-[11px] text-muted-foreground">Alucinación: <b className={o.halluc==="Media"?"text-warning":"text-foreground"}>{o.halluc}</b> · {o.cost}</p></button>})}</div></div>)}
        <details className="rounded-lg border border-info/20 bg-primary-soft p-4 text-sm text-muted-foreground"><summary className="cursor-pointer font-medium text-foreground"><ShieldCheck className="mr-2 inline size-4 text-primary"/>Filtro transversal de restricciones (se aplica antes de generar)</summary><div className="mt-3 flex flex-wrap gap-1.5">{restrictions.map(r=><span key={r} className="rounded-full bg-surface px-2.5 py-1 text-xs">{r}</span>)}</div></details>
      </div>}
      <div className="mt-7 flex justify-between border-t border-border pt-5"><Button variant="secondary" disabled={step===1} onClick={()=>setStep(s=>s-1)}>Anterior</Button>{step<4?<Button disabled={step===2&&mods.length===0||step===3&&!valid} onClick={()=>setStep(s=>s+1)}>Continuar<ChevronRight className="size-4"/></Button>:<Button disabled={!valid} onClick={()=>setLoading(true)}><Sparkles className="size-4"/>Generar curso con IA</Button>}</div></section>
    <p className="mt-4 flex items-center gap-2 text-xs text-muted-foreground"><CircleAlert className="size-4"/>SICCIA no genera formación médica, técnica especializada o de alto riesgo.</p></div>;
}

function Result({ go }: { go: (v: View) => void }) { const [open,setOpen]=useState([0]); const [downloaded,setDownloaded]=useState(false); const download=()=>{const blob=new Blob(["Paquete demostrativo SICCIA\nCurso: Fracciones para Básica Primaria\nIncluye programa, presentaciones, cuestionarios y laboratorios."],{type:"text/plain"}); const url=URL.createObjectURL(blob); const a=document.createElement("a");a.href=url;a.download="SICCIA_paquete_demostrativo.txt";a.click();URL.revokeObjectURL(url);setDownloaded(true)}; return <div className="space-y-5"><section className="glass-panel rounded-xl p-5"><div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center"><div><span className="inline-flex items-center gap-1 rounded-full bg-success-soft px-2.5 py-1 text-xs font-semibold text-success"><Check className="size-3"/>Generación completada</span><h2 className="mt-3 text-xl font-bold">Fracciones para Básica Primaria</h2><p className="mt-1 text-sm text-muted-foreground">6 horas · 3 módulos · Learning to do</p></div><Button onClick={download}><Download className="size-4"/>{downloaded?"Descargado":"Empaquetar y descargar"}</Button></div></section><div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]"><section className="glass-panel overflow-hidden rounded-xl"><div className="border-b border-border p-5"><h3 className="font-bold">Estructura modular</h3><p className="text-sm text-muted-foreground">Programa, presentaciones, cuestionarios y laboratorios listos para revisión.</p></div>{modules.map((m,i)=><div key={m.title} className="border-b border-border last:border-0"><button className="grid w-full grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 p-4 text-left hover:bg-muted" onClick={()=>setOpen(o=>o.includes(i)?o.filter(x=>x!==i):[...o,i])}>{open.includes(i)?<ChevronDown className="size-4"/>:<ChevronRight className="size-4"/>}<span className="truncate text-sm font-semibold">{m.title}</span><span className="text-xs text-muted-foreground">{m.duration}</span></button>{open.includes(i)&&<div className="space-y-2 bg-muted/50 px-4 pb-4 pt-1 sm:pl-11">{m.files.map(([name,type])=><div key={name} className="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 rounded-lg border border-border bg-surface p-3"><FileIcon type={type}/><span className="truncate text-sm">{name}</span><span className="text-xs font-bold text-muted-foreground">.{type.toLowerCase()}</span></div>)}</div>}</div>)}</section><aside className="space-y-4"><section className="glass-panel rounded-xl p-5"><div className="flex items-center justify-between"><h3 className="font-bold">Control de calidad</h3><ShieldCheck className="size-5 text-success"/></div><div className="mt-5 flex items-end gap-2"><span className="text-4xl font-bold text-success">94%</span><span className="pb-1 text-xs text-muted-foreground">veracidad validada</span></div><div className="mt-3 h-2 overflow-hidden rounded-full bg-muted"><div className="h-full w-[94%] bg-success"/></div><div className="mt-5 space-y-3 text-sm">{[["Coherencia pedagógica","97%"],["Fuentes oficiales","94%"],["Adecuación al nivel","91%"]].map(([a,b])=><div key={a} className="flex justify-between"><span className="text-muted-foreground">{a}</span><b>{b}</b></div>)}</div></section><section className="rounded-xl border border-warning/25 bg-warning-soft p-5"><CircleAlert className="size-5 text-warning"/><h3 className="mt-3 text-sm font-bold">1 observación para revisar</h3><p className="mt-1 text-xs leading-5 text-muted-foreground">Confirma el ejemplo del módulo 2 antes de aprobar el paquete. La fuente sugerida es el MEN.</p></section><Button className="w-full" variant="secondary" onClick={()=>go("dashboard")}>Volver al panel</Button></aside></div></div> }

function FileIcon({type}:{type:string}) { const Icon=type==="XLS"?FileSpreadsheet:type==="DOC"||type==="TXT"?FileText:File; return <span className="grid size-8 place-items-center rounded-md bg-primary-soft text-primary"><Icon className="size-4"/></span> }
function Quality(){const stats: Array<[string,string,LucideIcon]>=[["Promedio de veracidad","93%",ShieldCheck],["Cursos aprobados","21",Check],["Alertas por revisar","2",CircleAlert]];return <div className="space-y-5"><div><h2 className="text-xl font-bold">Historial de evaluaciones</h2><p className="text-sm text-muted-foreground">Resultados de veracidad, coherencia y adecuación pedagógica.</p></div><div className="grid gap-4 sm:grid-cols-3">{stats.map(([a,b,I])=><div key={a} className="glass-panel rounded-xl p-5"><I className="size-5 text-primary"/><p className="mt-4 text-2xl font-bold">{b}</p><p className="text-xs text-muted-foreground">{a}</p></div>)}</div><section className="glass-panel rounded-xl p-5"><h3 className="font-bold">Revisiones recientes</h3><div className="mt-4 space-y-3">{courses.map((c,i)=><div key={c.title} className="grid gap-2 rounded-lg border border-border p-4 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center"><div><p className="text-sm font-semibold">{c.title}</p><p className="text-xs text-muted-foreground">Evaluado frente a fuentes curriculares oficiales</p></div><span className={cn("text-sm font-bold",i===1?"text-warning":"text-success")}>{i===1?"88% · 1 alerta":`${96-i}% · Aprobado`}</span></div>)}</div></section></div>}
function SettingsView(){const [saved,setSaved]=useState(false);return <section className="glass-panel mx-auto max-w-2xl rounded-xl p-5 sm:p-7"><h2 className="text-xl font-bold">Preferencias del docente</h2><p className="mt-1 text-sm text-muted-foreground">Personaliza los valores sugeridos al crear un curso.</p><div className="mt-6 space-y-5"><Field label="Nombre visible" defaultValue="Marcela González"/><label className="block"><span className="mb-1.5 block text-sm font-medium">Institución</span><input className="h-11 w-full rounded-lg border border-input bg-surface px-3 text-sm" defaultValue="Institución Educativa San Rafael"/></label><label className="flex items-center justify-between gap-4 rounded-lg border border-border p-4"><span><b className="block text-sm">Notificaciones de calidad</b><span className="text-xs text-muted-foreground">Recibe alertas cuando un curso requiera revisión.</span></span><input type="checkbox" defaultChecked className="size-4 accent-primary"/></label><Button onClick={()=>setSaved(true)}>{saved?<><Check className="size-4"/>Cambios guardados</>:"Guardar preferencias"}</Button></div></section>}