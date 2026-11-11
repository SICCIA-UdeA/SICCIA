import { n as __toESM } from "../_runtime.mjs";
import { n as require_react } from "../_libs/@radix-ui/react-compose-refs+[...].mjs";
import { n as require_jsx_runtime } from "../_libs/radix-ui__react-context+react.mjs";
import { a as DialogOverlay$1, c as DialogTrigger$1, i as DialogDescription$1, l as Slot, n as DialogClose, o as DialogPortal$1, r as DialogContent$1, s as DialogTitle$1, t as Dialog$1 } from "../_libs/@radix-ui/react-dialog+[...].mjs";
import { a as Plus, c as LayoutDashboard, d as CircleAlert, f as ChevronRight, g as Bell, h as BookOpen, i as ShieldCheck, l as FileText, m as Bot, n as User, o as Menu, p as Check, r as Sparkles, s as LogOut, t as X, u as Download } from "../_libs/lucide-react.mjs";
import { n as clsx, t as cva } from "../_libs/class-variance-authority+clsx.mjs";
import { t as twMerge } from "../_libs/tailwind-merge.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-CENJmvhO.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function cn(...inputs) {
	return twMerge(clsx(inputs));
}
var buttonVariants = cva("inline-flex min-h-10 items-center justify-center gap-2 rounded-lg px-4 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50", {
	variants: {
		variant: {
			primary: "bg-primary text-primary-foreground hover:bg-primary-hover",
			default: "bg-primary text-primary-foreground hover:bg-primary-hover",
			secondary: "border border-border bg-surface text-foreground hover:bg-muted",
			outline: "border border-border bg-surface text-foreground hover:bg-muted",
			ghost: "text-muted-foreground hover:bg-muted hover:text-foreground",
			danger: "bg-destructive-soft text-destructive hover:bg-destructive-soft/70"
		},
		size: {
			default: "h-10",
			sm: "h-9 px-3 text-xs",
			icon: "size-10 p-0"
		}
	},
	defaultVariants: {
		variant: "primary",
		size: "default"
	}
});
var Button = (0, import_react.forwardRef)(({ className, variant, size, asChild, ...props }, ref) => {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(asChild ? Slot : "button", {
		ref,
		className: cn(buttonVariants({
			variant,
			size
		}), className),
		...props
	});
});
Button.displayName = "Button";
var Dialog = Dialog$1;
var DialogTrigger = DialogTrigger$1;
var DialogPortal = DialogPortal$1;
var DialogOverlay = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogOverlay$1, {
	ref,
	className: cn("fixed inset-0 z-50 bg-black/80  data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0", className),
	...props
}));
DialogOverlay.displayName = DialogOverlay$1.displayName;
var DialogContent = import_react.forwardRef(({ className, children, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogPortal, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogOverlay, {}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogContent$1, {
	ref,
	className: cn("fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 sm:rounded-lg", className),
	...props,
	children: [children, /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogClose, {
		className: "absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background cursor-pointer transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "h-4 w-4" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "sr-only",
			children: "Close"
		})]
	})]
})] }));
DialogContent.displayName = DialogContent$1.displayName;
var DialogHeader = ({ className, ...props }) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
	className: cn("flex flex-col space-y-1.5 text-center sm:text-left", className),
	...props
});
DialogHeader.displayName = "DialogHeader";
var DialogFooter = ({ className, ...props }) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
	className: cn("flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2", className),
	...props
});
DialogFooter.displayName = "DialogFooter";
var DialogTitle = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogTitle$1, {
	ref,
	className: cn("text-lg font-semibold leading-none tracking-tight", className),
	...props
}));
DialogTitle.displayName = DialogTitle$1.displayName;
var DialogDescription = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogDescription$1, {
	ref,
	className: cn("text-sm text-muted-foreground", className),
	...props
}));
DialogDescription.displayName = DialogDescription$1.displayName;
var BASE = {
	"BASE_URL": "/",
	"DEV": false,
	"MODE": "production",
	"PROD": true,
	"SSR": true,
	"TSS_DEV_SERVER": "false",
	"TSS_DEV_SSR_STYLES_BASEPATH": "/",
	"TSS_DEV_SSR_STYLES_ENABLED": "true",
	"TSS_DISABLE_CSRF_MIDDLEWARE_WARNING": "false",
	"TSS_INLINE_CSS_ENABLED": "false",
	"TSS_ROUTER_BASEPATH": "",
	"TSS_SERVER_FN_BASE": "/_serverFn/"
}["VITE_API_URL"]?.replace(/\/$/, "") || "/api";
var BACKEND_PORT = {
	"BASE_URL": "/",
	"DEV": false,
	"MODE": "production",
	"PROD": true,
	"SSR": true,
	"TSS_DEV_SERVER": "false",
	"TSS_DEV_SSR_STYLES_BASEPATH": "/",
	"TSS_DEV_SSR_STYLES_ENABLED": "true",
	"TSS_DISABLE_CSRF_MIDDLEWARE_WARNING": "false",
	"TSS_INLINE_CSS_ENABLED": "false",
	"TSS_ROUTER_BASEPATH": "",
	"TSS_SERVER_FN_BASE": "/_serverFn/"
}["VITE_BACKEND_PORT"] ?? "8084";
var ESTADOS_FINALES = [
	"completado",
	"completado_con_errores",
	"error"
];
var ApiError = class extends Error {
	status;
	constructor(message, status) {
		super(message);
		this.status = status;
	}
};
async function leerError(res) {
	let mensaje = [
		502,
		503,
		504
	].includes(res.status) ? `No se pudo conectar con el backend. Verifica que esté corriendo en localhost:${BACKEND_PORT}.` : `Error ${res.status} del servidor`;
	try {
		const body = await res.json();
		if (typeof body.detail === "string") mensaje = body.detail;
		else if (Array.isArray(body.detail)) mensaje = body.detail.map((d) => `${(d.loc ?? []).filter((x) => x !== "body").join(".")}: ${d.msg ?? ""}`).join(" | ");
	} catch {}
	return new ApiError(mensaje, res.status);
}
async function pedir(ruta, init) {
	let res;
	try {
		res = await fetch(`${BASE}${ruta}`, {
			credentials: "include",
			...init
		});
	} catch {
		throw new ApiError(`No se pudo conectar con el backend. Verifica que esté corriendo en localhost:${BACKEND_PORT}.`, 0);
	}
	if (!res.ok) throw await leerError(res);
	return await res.json();
}
function crearCurso(config, signal) {
	return pedir("/orquestador/cursos", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(config),
		signal: signal ?? null
	});
}
function estadoCurso(id, signal) {
	return pedir(`/orquestador/cursos/${encodeURIComponent(id)}`, { signal: signal ?? null });
}
async function descargarBlob(ruta, nombre) {
	let res;
	try {
		res = await fetch(`${BASE}${ruta}`, { credentials: "include" });
	} catch {
		throw new ApiError("No se pudo conectar con el backend.", 0);
	}
	if (!res.ok) throw await leerError(res);
	guardarBlob(await res.blob(), nombre);
}
function guardarBlob(blob, nombre) {
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = nombre;
	a.click();
	URL.revokeObjectURL(url);
}
function descargarZipPdf(id) {
	return descargarBlob(`/orquestador/cursos/${encodeURIComponent(id)}/descarga`, `curso_${id.slice(0, 8)}.zip`);
}
function descargarArchivo(id, nombre) {
	return descargarBlob(`/orquestador/cursos/${encodeURIComponent(id)}/archivos/${encodeURIComponent(nombre)}`, nombre);
}
async function usuarioActual(signal) {
	let res;
	try {
		res = await fetch(`${BASE}/auth/me`, {
			credentials: "include",
			cache: "no-store",
			signal: signal ?? null
		});
	} catch {
		throw new ApiError(`No se pudo conectar con el backend. Verifica que esté corriendo en localhost:${BACKEND_PORT}.`, 0);
	}
	if (res.status === 401) return null;
	if (!res.ok) throw await leerError(res);
	const body = await res.json();
	if (!body.authenticated || !body.id) return null;
	return {
		id: body.id,
		name: body.name ?? null,
		email: body.email ?? null,
		picture: body.picture ?? null
	};
}
var urlLoginGoogle = () => `${BASE}/auth/google`;
async function cerrarSesion() {
	const res = await fetch(`${BASE}/auth/logout`, {
		credentials: "include",
		cache: "no-store"
	});
	if (!res.ok) throw await leerError(res);
}
var limpio = (s) => s.trim();
var opcional = (s) => limpio(s) ? limpio(s) : null;
function construirConfigurador(f) {
	const modulos = f.modulos.map(limpio).filter(Boolean).map((titulo) => ({
		titulo,
		temas: []
	}));
	const actividades = f.actividades.map((a) => ({
		tipo: limpio(a.tipo),
		cantidad: Math.max(1, Math.trunc(a.cantidad) || 1),
		porcentaje: a.porcentaje
	}));
	const total = actividades.reduce((s, a) => s + a.cantidad, 0);
	return {
		datos: {
			tema: limpio(f.tema),
			publico_objetivo: opcional(f.publico),
			duracion_estimada: opcional(f.duracion),
			metodologia: opcional(f.metodologia)
		},
		contenido: {
			modulos_modo: modulos.length ? "manual" : "automatico",
			num_modulos: modulos.length || null,
			modulos,
			incluir_ejemplos_practicos: f.ejemplos,
			incluir_talleres_practica: f.talleres,
			incluir_cierre_por_modulo: f.cierre
		},
		evaluacion: {
			tipos_pregunta: f.tiposPregunta,
			actividades,
			total_actividades: total || null
		}
	};
}
function validarConfigurador(c) {
	const errores = [];
	if (c.datos.tema.length < 3) errores.push(`El nombre del curso debe tener al menos 3 caracteres.`);
	if (c.contenido.modulos.length > 20) errores.push(`Máximo 20 módulos.`);
	if (c.evaluacion.actividades.some((a) => a.tipo.length < 2)) errores.push("Cada actividad evaluativa necesita un tipo.");
	const dados = c.evaluacion.actividades.map((a) => a.porcentaje).filter((p) => p !== null);
	if (dados.some((p) => p < 0 || p > 100)) errores.push("Cada porcentaje debe estar entre 0 y 100.");
	const suma = dados.reduce((s, p) => s + p, 0);
	if (suma > 100.01) errores.push(`Los porcentajes suman ${suma}%, máximo 100%.`);
	else if (c.evaluacion.actividades.length && dados.length === c.evaluacion.actividades.length && Math.abs(suma - 100) > .01) errores.push(`Los porcentajes suman ${suma}%, deben sumar 100%.`);
	return errores;
}
var courses = [
	{
		initials: "JV",
		title: "Lenguaje de programación Java",
		meta: "Secundaria · 16 h · Learning to do",
		status: "Generado",
		tone: "success",
		progress: 100
	},
	{
		initials: "FR",
		title: "Fracciones para Básica Primaria",
		meta: "Primaria · 6 h · Resolución de problemas",
		status: "En revisión de calidad",
		tone: "warning",
		progress: 72
	},
	{
		initials: "EA",
		title: "Ecosistemas andinos y biodiversidad",
		meta: "Primaria · 4 h · Aprendizaje por proyectos",
		status: "Pendiente de aprobación",
		tone: "muted",
		progress: 38
	}
];
function Logo() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex items-center gap-2",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "grid size-9 place-items-center rounded-lg bg-primary text-sm font-bold text-primary-foreground shadow-sm",
			children: "S"
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "font-bold text-foreground",
			children: "SICCIA"
		})]
	});
}
function V2Mark({ children, className, label = "Para versión 2.0" }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: cn("relative", className),
		"aria-disabled": "true",
		title: label,
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			inert: true,
			className: "pointer-events-none h-full select-none opacity-40",
			children
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "pointer-events-none absolute inset-0 grid place-items-center overflow-hidden rounded-xl",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "-rotate-12 rounded-md border-2 border-primary/40 bg-surface/80 px-3 py-1 text-xs font-bold uppercase tracking-wider text-primary sm:text-sm",
				children: label
			})
		})]
	});
}
function Index() {
	const [user, setUser] = (0, import_react.useState)(null);
	const [checking, setChecking] = (0, import_react.useState)(true);
	const [view, setView] = (0, import_react.useState)("dashboard");
	const [mobileMenu, setMobileMenu] = (0, import_react.useState)(false);
	const [collapsed, setCollapsed] = (0, import_react.useState)(false);
	const [noticeOpen, setNoticeOpen] = (0, import_react.useState)(false);
	const [logoutError, setLogoutError] = (0, import_react.useState)(null);
	(0, import_react.useEffect)(() => {
		const ctrl = new AbortController();
		usuarioActual(ctrl.signal).then((u) => setUser(u)).catch(() => setUser(null)).finally(() => {
			if (!ctrl.signal.aborted) setChecking(false);
		});
		return () => ctrl.abort();
	}, []);
	const logout = async () => {
		let error = null;
		if (user && !isDemo(user)) try {
			await cerrarSesion();
		} catch (e) {
			error = e instanceof Error ? e.message : "No se pudo cerrar la sesión del servidor.";
		}
		setUser(null);
		setView("dashboard");
		setMobileMenu(false);
		setCollapsed(false);
		setNoticeOpen(false);
		setLogoutError(error);
	};
	if (checking) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("main", {
		className: "grid min-h-screen place-items-center bg-background",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex flex-col items-center gap-3",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Logo, {}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm text-muted-foreground",
				children: "Verificando sesión..."
			})]
		})
	});
	if (!user) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthScreen, {
		initialError: logoutError,
		onLogin: (u) => {
			setLogoutError(null);
			setUser(u);
			setView("dashboard");
		}
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AppShell, {
		user,
		view,
		setView,
		mobileMenu,
		setMobileMenu,
		collapsed,
		setCollapsed,
		noticeOpen,
		setNoticeOpen,
		onLogout: () => void logout()
	});
}
var DEMO_USER = {
	id: "demo",
	name: "Docente de Prueba",
	email: "prueba@siccia.local",
	picture: null
};
var isDemo = (u) => u.id === DEMO_USER.id;
var LOGIN_POLL_MS = 1500;
var LOGIN_TIMEOUT_MS = 3e5;
function AuthScreen({ onLogin, initialError }) {
	const [waiting, setWaiting] = (0, import_react.useState)(false);
	const [error, setError] = (0, import_react.useState)(initialError);
	const popupRef = (0, import_react.useRef)(null);
	const timerRef = (0, import_react.useRef)(void 0);
	const wrongHost = typeof window !== "undefined" && window.location.hostname === "127.0.0.1";
	(0, import_react.useEffect)(() => () => {
		window.clearTimeout(timerRef.current);
		popupRef.current?.close();
	}, []);
	const stop = (msg) => {
		window.clearTimeout(timerRef.current);
		setWaiting(false);
		setError(msg);
	};
	const loginGoogle = () => {
		setError(null);
		const popup = window.open(urlLoginGoogle(), "siccia-google", "width=500,height=650");
		if (!popup) {
			window.location.href = urlLoginGoogle();
			return;
		}
		popupRef.current = popup;
		setWaiting(true);
		const started = Date.now();
		const tick = async () => {
			try {
				const u = await usuarioActual();
				if (u) {
					popup.close();
					stop(null);
					onLogin(u);
					return;
				}
			} catch (e) {
				popup.close();
				stop(e instanceof Error ? e.message : "No se pudo verificar la sesión.");
				return;
			}
			if (popup.closed) {
				stop("No se completó el inicio de sesión. Intenta de nuevo.");
				return;
			}
			if (Date.now() - started > LOGIN_TIMEOUT_MS) {
				popup.close();
				stop("El inicio de sesión tardó demasiado. Intenta de nuevo.");
				return;
			}
			timerRef.current = window.setTimeout(() => void tick(), LOGIN_POLL_MS);
		};
		timerRef.current = window.setTimeout(() => void tick(), LOGIN_POLL_MS);
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "relative grid min-h-screen place-items-center overflow-hidden bg-background px-4 py-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "absolute inset-x-0 top-0 h-1 bg-primary" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "absolute left-[8%] top-[10%] size-72 rounded-full bg-primary-soft/70 blur-3xl" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "glass-panel relative z-10 w-full max-w-md rounded-2xl p-6 text-center sm:p-8",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "mb-8 flex justify-center",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Logo, {})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "text-2xl font-bold",
						children: "Bienvenidos a SICCIA"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-sm text-muted-foreground",
						children: "Usa tu cuenta de Google para ingresar al panel docente."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						variant: "outline",
						className: "mt-8 h-11 w-full border-border bg-surface text-foreground shadow-sm hover:bg-muted hover:text-foreground",
						disabled: waiting,
						onClick: loginGoogle,
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GoogleMark, { className: "size-4" }), waiting ? "Esperando a Google..." : "Iniciar sesión con Google"]
					}),
					waiting && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 text-xs text-muted-foreground",
						children: "Completa el inicio de sesión en la ventana de Google."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-6 flex items-center gap-3",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "h-px flex-1 bg-border" }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-xs text-muted-foreground",
								children: "solo para pruebas"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "h-px flex-1 bg-border" })
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						variant: "ghost",
						className: "mt-3 w-full border border-dashed border-border text-muted-foreground",
						disabled: waiting,
						onClick: () => onLogin(DEMO_USER),
						children: "Acceso simulado"
					}),
					error && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 text-xs text-destructive",
						children: error
					}),
					wrongHost && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-3 rounded-lg bg-warning-soft p-2 text-xs text-muted-foreground",
						children: [
							"Abre la aplicación en ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("b", { children: ["http://localhost:", {
								"BASE_URL": "/",
								"DEV": false,
								"MODE": "production",
								"PROD": true,
								"SSR": true,
								"TSS_DEV_SERVER": "false",
								"TSS_DEV_SSR_STYLES_BASEPATH": "/",
								"TSS_DEV_SSR_STYLES_ENABLED": "true",
								"TSS_DISABLE_CSRF_MIDDLEWARE_WARNING": "false",
								"TSS_INLINE_CSS_ENABLED": "false",
								"TSS_ROUTER_BASEPATH": "",
								"TSS_SERVER_FN_BASE": "/_serverFn/"
							}["VITE_FRONTEND_PORT"] ?? "8085"] }),
							" para que el inicio de sesión funcione."
						]
					})
				]
			})
		]
	});
}
function GoogleMark({ className }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("svg", {
		className,
		viewBox: "0 0 24 24",
		"aria-hidden": "true",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", {
				fill: "#4285F4",
				d: "M23.5 12.27c0-.85-.08-1.66-.22-2.45H12v4.64h6.45a5.52 5.52 0 0 1-2.39 3.62v3h3.87c2.26-2.09 3.57-5.16 3.57-8.81Z"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", {
				fill: "#34A853",
				d: "M12 24c3.24 0 5.96-1.07 7.94-2.91l-3.87-3c-1.08.72-2.45 1.15-4.07 1.15-3.13 0-5.78-2.11-6.73-4.96H1.29v3.1A12 12 0 0 0 12 24Z"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", {
				fill: "#FBBC05",
				d: "M5.27 14.28a7.2 7.2 0 0 1 0-4.56v-3.1H1.29a12 12 0 0 0 0 10.76l3.98-3.1Z"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", {
				fill: "#EA4335",
				d: "M12 4.76c1.76 0 3.34.6 4.58 1.79l3.44-3.44A11.98 11.98 0 0 0 12 0 12 12 0 0 0 1.29 6.62l3.98 3.1C6.22 6.87 8.87 4.76 12 4.76Z"
			})
		]
	});
}
function Field({ label, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
		className: "block",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "mb-1.5 block text-sm font-medium",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
			className: "h-11 w-full rounded-lg border border-input bg-surface px-3 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/15",
			required: true,
			...props
		})]
	});
}
var nav = [
	[
		"dashboard",
		"Panel principal",
		LayoutDashboard
	],
	[
		"courses",
		"Mis cursos",
		BookOpen
	],
	[
		"generator",
		"Generar nuevo curso",
		Sparkles
	],
	[
		"settings",
		"Información personal",
		User
	]
];
function displayName(u) {
	return u.name?.trim() || u.email || "Docente";
}
function shortName(u) {
	const parts = displayName(u).split(/\s+/).filter(Boolean);
	const next = parts.slice(1).find((w) => /^\p{Lu}/u.test(w));
	return next && !displayName(u).includes("@") ? `${parts[0]} ${next[0]}.` : parts[0] ?? displayName(u);
}
function initials(u) {
	const parts = displayName(u).split(/[\s@.]+/).filter(Boolean);
	const next = parts.slice(1).find((w) => /^\p{Lu}/u.test(w)) ?? parts[1];
	return ((parts[0]?.[0] ?? "") + (next?.[0] ?? "")).toUpperCase() || "D";
}
function UserAvatar({ user }) {
	const [failed, setFailed] = (0, import_react.useState)(false);
	if (user.picture && !failed) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("img", {
		src: user.picture,
		alt: "",
		referrerPolicy: "no-referrer",
		onError: () => setFailed(true),
		className: "size-8 rounded-md object-cover"
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		className: "grid size-8 place-items-center rounded-md bg-primary-soft text-xs font-bold text-primary",
		children: initials(user)
	});
}
var credits = [
	{
		name: "Juan Esteban Tobon Martinez",
		email: "esteban.tobon2@udea.edu.co"
	},
	{
		name: "Steven Aguirre Giraldo",
		email: "steven.aguirreg@udea.edu.co"
	},
	{
		name: "Luis Fernando Alvarez Padilla",
		email: "luis.alvarezp@udea.edu.co"
	}
];
function CreditsDialog() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Dialog, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogTrigger, {
		asChild: true,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
			className: "text-xs text-muted-foreground",
			variant: "ghost",
			size: "sm",
			children: "Créditos"
		})
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogContent, {
		className: "max-w-md rounded-xl",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DialogHeader, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogTitle, { children: "Créditos del proyecto" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DialogDescription, { children: "Hecho por:" })] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "grid gap-3",
				children: credits.map(({ name, email }) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "rounded-lg border border-border bg-surface p-3",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "font-semibold",
						children: name
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("a", {
						className: "mt-1 block break-all text-sm text-primary hover:underline",
						href: `mailto:${email}`,
						children: email
					})]
				}, email))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "border-t border-border pt-4 text-center text-sm font-semibold text-muted-foreground",
				children: "Facultad de Ingeniería UdeA"
			})
		]
	})] });
}
function AppShell(props) {
	const { user, view, setView, mobileMenu, setMobileMenu, collapsed, setCollapsed, noticeOpen, setNoticeOpen, onLogout } = props;
	const title = {
		dashboard: "Panel principal",
		courses: "Mis cursos",
		generator: "Generar nuevo curso",
		settings: "Información personal",
		result: "Curso generado"
	}[view];
	const [job, setJob] = (0, import_react.useState)(null);
	const [jobConfig, setJobConfig] = (0, import_react.useState)(null);
	const go = (v) => {
		setView(v);
		setMobileMenu(false);
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "min-h-screen bg-background text-foreground",
		children: [
			mobileMenu && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
				"aria-label": "Cerrar menú",
				className: "fixed inset-0 z-30 bg-foreground/20 lg:hidden",
				onClick: () => setMobileMenu(false)
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("aside", {
				className: cn("fixed inset-y-0 left-0 z-40 flex flex-col border-r border-border bg-surface/95 p-3 backdrop-blur-xl transition-[width,transform] lg:translate-x-0", mobileMenu ? "translate-x-0" : "-translate-x-full", collapsed ? "w-20" : "w-64"),
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "grid grid-cols-[minmax(0,1fr)_auto] items-center px-2 py-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: cn("min-w-0 overflow-hidden", collapsed && "lg:w-9"),
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Logo, {})
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							className: "lg:hidden",
							size: "icon",
							variant: "ghost",
							onClick: () => setMobileMenu(false),
							"aria-label": "Cerrar menú",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "size-5" })
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("nav", {
						className: "mt-5 space-y-1",
						children: nav.map(([id, label, Icon]) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
							onClick: () => go(id),
							title: label,
							className: cn("flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors", view === id ? "bg-primary-soft text-primary" : "text-muted-foreground hover:bg-muted hover:text-foreground", collapsed && "lg:justify-center lg:px-0"),
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, { className: "size-4 shrink-0" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: cn("truncate", collapsed && "lg:hidden"),
								children: label
							})]
						}, id))
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						className: "mt-auto w-full",
						variant: "ghost",
						onClick: onLogout,
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LogOut, { className: "size-4" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: cn(collapsed && "lg:hidden"),
							children: "Cerrar sesión"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						className: "absolute -right-4 top-20 hidden rounded-full bg-surface shadow-sm lg:inline-flex",
						size: "icon",
						variant: "secondary",
						onClick: () => setCollapsed(!collapsed),
						"aria-label": collapsed ? "Expandir menú" : "Contraer menú",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronRight, { className: cn("size-4 transition-transform", !collapsed && "rotate-180") })
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: cn("transition-[margin]", collapsed ? "lg:ml-20" : "lg:ml-64"),
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
					className: "sticky top-0 z-20 grid h-16 grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 border-b border-border bg-surface/80 px-4 backdrop-blur-xl sm:px-6",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							className: "lg:hidden",
							size: "icon",
							variant: "ghost",
							onClick: () => setMobileMenu(true),
							"aria-label": "Abrir menú",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Menu, { className: "size-5" })
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "min-w-0",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
								className: "truncate text-base font-bold sm:text-lg",
								children: title
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "hidden truncate text-xs text-muted-foreground sm:block",
								children: "Panel docente · Institución Educativa San Rafael"
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "relative flex shrink-0 items-center gap-2",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CreditsDialog, {}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
									size: "icon",
									variant: "secondary",
									"aria-label": "Notificaciones",
									onClick: () => setNoticeOpen(!noticeOpen),
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bell, { className: "size-4" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "absolute right-0 top-0 size-2 rounded-full bg-warning" })]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center gap-2 rounded-lg border border-border bg-surface p-1 pr-2",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(UserAvatar, { user }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "hidden max-w-40 truncate text-sm font-semibold sm:inline",
											children: shortName(user)
										}),
										isDemo(user) && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "rounded-full bg-warning-soft px-2 py-0.5 text-[10px] font-bold uppercase text-warning",
											children: "Prueba"
										})
									]
								}),
								noticeOpen && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "glass-panel absolute right-0 top-12 w-72 rounded-xl p-4",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "font-semibold",
										children: "Notificaciones"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "mt-3 rounded-lg bg-warning-soft p-3 text-xs text-muted-foreground",
										children: "El curso de Fracciones tiene una observación de calidad pendiente."
									})]
								})
							]
						})
					]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
					className: "mx-auto max-w-6xl p-4 sm:p-6",
					children: [
						view === "dashboard" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Dashboard, { go }),
						" ",
						view === "courses" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Courses, { go }),
						" ",
						view === "generator" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Generator, { onComplete: (t, c) => {
							setJob(t);
							setJobConfig(c);
							go("result");
						} }),
						" ",
						view === "settings" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SettingsView, { user }),
						" ",
						view === "result" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Result, {
							go,
							job,
							config: jobConfig
						})
					]
				})]
			})
		]
	});
}
function Dashboard({ go }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-5",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "grid gap-4 sm:grid-cols-2",
				children: [[
					"Cursos generados",
					"24",
					"+3 esta semana",
					BookOpen
				], [
					"Borradores activos",
					"6",
					"2 en revisión",
					FileText
				]].map(([label, value, detail, Icon]) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(V2Mark, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "glass-panel h-full rounded-xl p-5",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-start justify-between",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-xs font-semibold uppercase text-muted-foreground",
								children: label
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-2 text-3xl font-bold text-primary",
								children: value
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-1 text-xs text-muted-foreground",
								children: detail
							})
						] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "grid size-10 place-items-center rounded-lg bg-primary-soft text-primary",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, { className: "size-5" })
						})]
					})
				}) }, label))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "glass-panel overflow-hidden rounded-xl",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 border-b border-border p-4 sm:p-5",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "min-w-0",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
							className: "font-bold",
							children: "Cursos recientes"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-xs text-muted-foreground",
							children: "Historial de cursos disponible en la versión 2.0."
						})]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						size: "sm",
						onClick: () => go("generator"),
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Plus, { className: "size-4" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "hidden sm:inline",
							children: "Generar curso"
						})]
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(V2Mark, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CourseList, {}) })]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "rounded-xl border border-primary bg-primary p-5 text-primary-foreground shadow-lg",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Sparkles, { className: "size-6" }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "mt-4 text-lg font-bold",
						children: "Convierte una idea en una secuencia didáctica."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-sm text-primary-foreground/80",
						children: "Define el tema, la audiencia y la metodología. SICCIA organiza el resto."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						className: "mt-5 bg-surface text-primary hover:bg-primary-soft",
						onClick: () => go("generator"),
						children: ["Comenzar ahora", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronRight, { className: "size-4" })]
					})
				]
			})
		]
	});
}
function CourseList() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "divide-y divide-border",
		children: courses.map((c) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "grid grid-cols-[auto_minmax(0,1fr)] gap-3 p-4 sm:grid-cols-[auto_minmax(0,1fr)_auto] sm:items-center sm:px-5",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "grid size-10 shrink-0 place-items-center rounded-lg bg-primary-soft text-xs font-bold text-primary",
					children: c.initials
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "min-w-0",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "truncate text-sm font-semibold",
						children: c.title
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "truncate text-xs text-muted-foreground",
						children: c.meta
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "col-start-2 flex items-center gap-3 sm:col-auto",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "h-1.5 w-20 overflow-hidden rounded-full bg-muted",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: cn("h-full", c.tone === "success" ? "bg-success" : c.tone === "warning" ? "bg-warning" : "bg-primary"),
							style: { width: `${c.progress}%` }
						})
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: cn("w-32 text-right text-xs font-semibold", c.tone === "success" ? "text-success" : c.tone === "warning" ? "text-warning" : "text-muted-foreground"),
						children: c.status
					})]
				})
			]
		}, c.title))
	});
}
function Courses({ go }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "text-xl font-bold",
				children: "Biblioteca de cursos"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm text-muted-foreground",
				children: "La biblioteca estará disponible en la versión 2.0."
			})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
				onClick: () => go("generator"),
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Plus, { className: "size-4" }), "Nuevo"]
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(V2Mark, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
			className: "glass-panel overflow-hidden rounded-xl",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CourseList, {})
		}) })]
	});
}
var activityTypes = [
	"Examen",
	"Laboratorio",
	"Investigación",
	"Quiz"
];
var questionTypeOptions = [
	"Selección múltiple",
	"Falso/verdadero",
	"Pregunta abierta",
	"Matching"
];
var durationLabels = {
	corto: "4-6 horas",
	largo: "12-16 horas"
};
var viaLabels = {
	programa: "Programa",
	contenido: "Contenido",
	evaluacion: "Evaluación",
	verificacion: "Verificación"
};
({ ...viaLabels });
var viaStatusLabels = {
	pendiente: "Pendiente",
	en_curso: "En curso",
	completada: "Completada",
	omitida: "Omitida"
};
var viaCompletada = (estado) => estado === "completada" || estado?.startsWith("completada (") === true;
var viaStatusLabel = (estado) => viaCompletada(estado) ? "Completada" : viaStatusLabels[estado] ?? estado;
var estadoLabels = {
	pendiente: "Pendiente",
	planificando: "Planificando",
	ejecutando: "Ejecutando",
	completado: "Generación completada",
	completado_con_errores: "Completado con errores",
	error: "Error"
};
var POLL_MS = 1500;
var MAX_POLL_MS = 36e5;
var restrictions = [
	"Educación superior",
	"Formación profesional especializada",
	"Certificaciones",
	"Medicina clínica",
	"Gastronomía profesional",
	"Actividades peligrosas",
	"Asesoría profesional",
	"Persuasión política/religiosa",
	"Contenido sexual",
	"Actividades ilícitas",
	"Contenido no verificable"
];
function Chip({ active, onClick, children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
		type: "button",
		onClick,
		className: cn("rounded-lg border px-3 py-2 text-sm transition-colors", active ? "border-primary bg-primary-soft text-primary" : "border-border bg-surface hover:bg-muted"),
		children: [active && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "mr-1 inline size-3.5" }), children]
	});
}
function Auto({ items }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "flex flex-wrap gap-1.5",
		children: items.map((i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
			className: "rounded-full bg-muted px-2.5 py-1 text-xs text-muted-foreground",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Sparkles, { className: "mr-1 inline size-3 text-primary" }), i]
		}, i))
	});
}
function Generator({ onComplete }) {
	const [step, setStep] = (0, import_react.useState)(1);
	const [tema, setTema] = (0, import_react.useState)("");
	const [duration, setDuration] = (0, import_react.useState)("");
	const [audience, setAudience] = (0, import_react.useState)("");
	const [method, setMethod] = (0, import_react.useState)("");
	const [closure, setClosure] = (0, import_react.useState)(true);
	const [examples, setExamples] = (0, import_react.useState)(true);
	const [workshops, setWorkshops] = (0, import_react.useState)(true);
	const [mods, setMods] = (0, import_react.useState)([]);
	const [newMod, setNewMod] = (0, import_react.useState)("");
	const [questionTypes, setQuestionTypes] = (0, import_react.useState)([]);
	const [acts, setActs] = (0, import_react.useState)([]);
	const [loading, setLoading] = (0, import_react.useState)(false);
	const [jobId, setJobId] = (0, import_react.useState)(null);
	const [job, setJob] = (0, import_react.useState)(null);
	const [apiError, setApiError] = (0, import_react.useState)(null);
	const sentConfig = (0, import_react.useRef)(null);
	const onCompleteRef = (0, import_react.useRef)(onComplete);
	onCompleteRef.current = onComplete;
	const durationOptions = [[
		"corto",
		"Curso corto",
		"4–6 horas · tema puntual"
	], [
		"largo",
		"Curso largo",
		"12–16 horas · unidad completa"
	]];
	(0, import_react.useEffect)(() => {
		if (!jobId) return;
		const ctrl = new AbortController();
		let timer;
		const startedAt = Date.now();
		const tick = async () => {
			try {
				const t = await estadoCurso(jobId, ctrl.signal);
				setJob(t);
				if (Date.now() - startedAt >= MAX_POLL_MS && !ESTADOS_FINALES.includes(t.estado)) {
					setApiError("El trabajo tardó demasiado. Revisa el backend y vuelve a intentarlo.");
					return;
				}
				if (!ESTADOS_FINALES.includes(t.estado)) {
					timer = window.setTimeout(tick, POLL_MS);
					return;
				}
				if (t.estado !== "error" && sentConfig.current) {
					const cfg = sentConfig.current;
					timer = window.setTimeout(() => onCompleteRef.current(t, cfg), 450);
				}
			} catch (e) {
				if (!ctrl.signal.aborted) setApiError(e instanceof Error ? e.message : "Error consultando el estado del trabajo.");
			}
		};
		tick();
		return () => {
			ctrl.abort();
			window.clearTimeout(timer);
		};
	}, [jobId]);
	const addMod = () => {
		if (newMod.trim() && mods.length < 20) {
			setMods((m) => [...m, newMod.trim()]);
			setNewMod("");
		}
	};
	const removeMod = (i) => setMods((m) => m.filter((_, j) => j !== i));
	const updAct = (i, patch) => setActs((a) => a.map((x, j) => j === i ? {
		...x,
		...patch
	} : x));
	const toggleQuestion = (q) => setQuestionTypes((qs) => qs.includes(q) ? qs.filter((x) => x !== q) : [...qs, q]);
	const config = construirConfigurador({
		tema,
		publico: audience,
		duracion: durationLabels[duration] ?? "",
		metodologia: method,
		modulos: mods,
		ejemplos: examples,
		talleres: workshops,
		cierre: closure,
		tiposPregunta: questionTypes,
		actividades: acts
	});
	const errors = validarConfigurador(config);
	const evalErrors = errors.filter((e) => /porcentaje|actividad/i.test(e));
	const stepValid = [
		tema.trim().length >= 3,
		mods.length <= 20,
		evalErrors.length === 0,
		errors.length === 0
	];
	const pctSum = acts.reduce((s, a) => s + (a.porcentaje ?? 0), 0);
	const generate = async () => {
		if (errors.length) return;
		sentConfig.current = config;
		setJob(null);
		setJobId(null);
		setApiError(null);
		setLoading(true);
		try {
			setJobId((await crearCurso(config)).id);
		} catch (e) {
			setApiError(e instanceof Error ? e.message : "No se pudo crear el trabajo.");
		}
	};
	const reset = () => {
		setLoading(false);
		setJobId(null);
		setJob(null);
		setApiError(null);
	};
	const viaKeys = job && Object.keys(job.vias).length ? Object.keys(job.vias) : Object.keys(viaLabels).filter((k) => k !== "verificacion");
	const doneVias = viaKeys.filter((k) => {
		const v = job?.vias[k];
		return !!v && v !== "en_curso" && v !== "pendiente";
	}).length;
	const progress = !job ? 5 : job.estado === "pendiente" ? 10 : job.estado === "planificando" ? 25 : job.estado === "ejecutando" ? 40 + Math.round(doneVias / viaKeys.length * 55) : 100;
	const stepState = (key) => {
		if (key === "plan") return !job || job.estado === "pendiente" ? "wait" : job.estado === "planificando" ? "active" : job.estado === "error" && !Object.keys(job.vias).length ? "fail" : "done";
		const v = job?.vias[key];
		return !v || v === "pendiente" || v === "omitida" ? "wait" : v === "en_curso" ? "active" : viaCompletada(v) ? "done" : "fail";
	};
	const phases = [["plan", "Planificación del curso"], ...viaKeys.map((k) => [k, `Vía ${viaLabels[k] ?? k}`])];
	const failed = apiError ?? (job?.estado === "error" ? job.error ?? "La generación falló." : null);
	if (loading) return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		className: "glass-panel mx-auto max-w-2xl rounded-xl p-8 text-center sm:p-12",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: cn("mx-auto grid size-16 place-items-center rounded-full", failed ? "bg-warning-soft" : "bg-primary-soft"),
				children: failed ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleAlert, { className: "size-7 text-warning" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bot, { className: "size-7 spin-slow text-primary" })
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "mt-6 text-xl font-bold",
				children: failed ? "No se pudo generar el curso" : "Orquestando tu curso"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-sm text-muted-foreground",
				children: failed ?? (job ? `Trabajo ${job.id.slice(0, 8)} · estado: ${estadoLabels[job.estado]}` : "Enviando configuración al backend...")
			}),
			!!job?.advertencias.length && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mx-auto mt-4 max-w-md list-disc space-y-1 pl-5 text-left text-xs text-muted-foreground",
				children: job.advertencias.map((advertencia, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: advertencia }, `${i}-${advertencia}`))
			}),
			!failed && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mx-auto mt-7 h-2 max-w-md overflow-hidden rounded-full bg-muted",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "h-full bg-primary transition-all",
					style: { width: `${progress}%` }
				})
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
				className: "mt-3 text-sm font-semibold text-primary",
				children: [progress, "%"]
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-8 grid gap-2 text-left sm:grid-cols-2",
				children: phases.map(([k, x]) => {
					const s = stepState(k);
					return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: cn("rounded-lg border p-3 text-xs", s === "done" ? "border-success/20 bg-success-soft text-success" : s === "active" ? "border-primary/30 bg-primary-soft text-primary pulse-soft" : s === "fail" ? "border-destructive/30 bg-warning-soft text-destructive" : "border-border bg-muted text-muted-foreground"),
						children: [
							s === "done" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "mr-1 inline size-3" }),
							s === "fail" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "mr-1 inline size-3" }),
							x
						]
					}, k);
				})
			}),
			failed && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-7 flex flex-wrap justify-center gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					variant: "secondary",
					onClick: reset,
					children: "Volver al configurador"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					onClick: generate,
					children: "Reintentar"
				})]
			})
		]
	});
	const titles = [
		"Programa del curso",
		"Módulos y temas",
		"Evaluaciones",
		"Revisión y envío"
	];
	const yesNo = (label, hint, value, set) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex items-center justify-between gap-4 rounded-lg border border-border bg-surface p-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "text-sm font-semibold",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "text-xs text-muted-foreground",
			children: hint
		})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex gap-2",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Chip, {
				active: value,
				onClick: () => set(true),
				children: "Sí"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Chip, {
				active: !value,
				onClick: () => set(false),
				children: "No"
			})]
		})]
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mx-auto max-w-4xl",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mb-5 flex items-center justify-between gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "text-xl font-bold",
					children: "Configurador GIA"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-sm text-muted-foreground",
					children: "Basado en el modelo de curso SICCIA (Matriz 1) y la evaluación de IAs (Matriz 2)."
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "shrink-0 rounded-full bg-primary-soft px-3 py-1 text-xs font-semibold text-primary",
					children: [
						"Paso ",
						step,
						" de 4"
					]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mb-6 grid grid-cols-4 gap-2",
				children: titles.map((t, n) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: cn("h-1.5 rounded-full", n + 1 <= step ? "bg-primary" : "bg-muted") }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: cn("mt-1.5 hidden text-xs sm:block", n + 1 === step ? "font-semibold text-primary" : "text-muted-foreground"),
					children: t
				})] }, t))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "glass-panel rounded-xl p-5 sm:p-7",
				children: [
					step === 1 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "space-y-5",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
								className: "font-bold",
								children: "Nivel 1 · Programa del curso"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-sm text-muted-foreground",
								children: "Campos configurables del programa."
							})] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
								label: "Nombre del curso",
								type: "text",
								value: tema,
								onChange: (e) => setTema(e.target.value),
								minLength: 3,
								placeholder: "Ej.: Introducción a la programación"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "-mt-3 text-xs text-muted-foreground",
								children: "Los campos que dejes vacíos los completa la IA."
							}),
							tema.length > 0 && tema.trim().length < 3 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "-mt-3 text-xs text-destructive",
								children: [
									"Mínimo ",
									3,
									" caracteres."
								]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
								className: "block",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "mb-1.5 block text-sm font-medium",
									children: ["Dirigido a / público objetivo ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "font-normal text-muted-foreground",
										children: "(opcional)"
									})]
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("select", {
									value: audience,
									onChange: (e) => setAudience(e.target.value),
									className: cn("h-11 w-full rounded-lg border border-input bg-surface px-3 text-sm", !audience && "text-muted-foreground"),
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
											value: "",
											children: "Selecciona el público"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", { children: "Básica primaria · Grados 3.º a 5.º" }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", { children: "Básica secundaria · Grados 6.º a 9.º" }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", { children: "Media · Grados 10.º y 11.º" }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", { children: "Tutores y formadores independientes" })
									]
								})]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: "text-sm font-medium",
								children: ["Duración ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-normal text-muted-foreground",
									children: "(opcional)"
								})]
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "mt-2 grid gap-3 sm:grid-cols-2",
								children: durationOptions.map(([id, t, d]) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
									onClick: () => setDuration((d) => d === id ? "" : id),
									className: cn("rounded-lg border p-4 text-left", duration === id ? "border-primary bg-primary-soft" : "border-border bg-surface hover:bg-muted"),
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "text-sm font-semibold",
										children: t
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "mt-1 text-xs text-muted-foreground",
										children: d
									})]
								}, id))
							})] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: "text-sm font-medium",
								children: ["Metodología de aprendizaje ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-normal text-muted-foreground",
									children: "(opcional)"
								})]
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "mt-2 flex flex-wrap gap-2",
								children: [
									"Learning to do",
									"Aprendizaje por proyectos",
									"Resolución de problemas",
									"Aula invertida"
								].map((x) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Chip, {
									active: method === x,
									onClick: () => setMethod((m) => m === x ? "" : x),
									children: x
								}, x))
							})] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "rounded-lg border border-border bg-muted/50 p-4",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
									className: "mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground",
									children: "Generado automáticamente por la IA"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Auto, { items: [
									"Descripción / introducción",
									"Justificación",
									"Objetivo general",
									"Objetivos específicos (máx. 4)",
									"Resultados de aprendizaje",
									"Requisitos previos",
									"Bibliografía y fuentes"
								] })]
							})
						]
					}),
					step === 2 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "space-y-5",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
								className: "font-bold",
								children: "Niveles 2 y 3 · Módulos y temas"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "text-sm text-muted-foreground",
								children: [
									"Define la lista de módulos (máx. ",
									20,
									"); la IA genera los temas de cada uno. Sin módulos, la IA los diseña."
								]
							})] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "space-y-2",
								children: mods.map((m, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center gap-3 rounded-lg border border-border bg-surface p-3",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "grid size-7 shrink-0 place-items-center rounded-md bg-primary-soft text-xs font-bold text-primary",
											children: i + 1
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
											"aria-label": `Módulo ${i + 1}`,
											value: m,
											onChange: (e) => setMods((ms) => ms.map((x, j) => j === i ? e.target.value : x)),
											className: "min-w-0 flex-1 bg-transparent text-sm outline-none"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
											"aria-label": "Quitar módulo",
											onClick: () => removeMod(i),
											className: "rounded p-1 text-muted-foreground hover:bg-muted",
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "size-4" })
										})
									]
								}, i))
							}),
							mods.length === 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "rounded-lg bg-primary-soft p-3 text-xs text-primary",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Sparkles, { className: "mr-1 inline size-3" }), "Modo automático: la IA definirá los módulos."]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex gap-2",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
									value: newMod,
									onChange: (e) => setNewMod(e.target.value),
									onKeyDown: (e) => e.key === "Enter" && addMod(),
									placeholder: "Nombre del nuevo módulo",
									className: "h-10 min-w-0 flex-1 rounded-lg border border-input bg-surface px-3 text-sm"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
									variant: "secondary",
									disabled: mods.length >= 20,
									onClick: addMod,
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Plus, { className: "size-4" }), "Agregar"]
								})]
							}),
							yesNo("Cierre por módulo", "Genera un resumen al final de cada módulo.", closure, setClosure),
							yesNo("Ejemplos prácticos", "Incluye ejemplos en cada tema.", examples, setExamples),
							yesNo("Talleres de práctica", "Un taller sin nota por módulo.", workshops, setWorkshops),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "grid gap-3 sm:grid-cols-2",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "rounded-lg border border-border bg-muted/50 p-4",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground",
										children: "Por cada módulo"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Auto, { items: [
										"Introducción",
										"Objetivos",
										"Temas",
										...closure ? ["Resumen / cierre"] : [],
										...workshops ? ["Taller de práctica"] : []
									] })]
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "rounded-lg border border-border bg-muted/50 p-4",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground",
										children: "Por cada tema"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Auto, { items: [
										"Explicación",
										"Diapositivas",
										...examples ? ["Ejemplo"] : []
									] })]
								})]
							})
						]
					}),
					step === 3 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "space-y-5",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
								className: "font-bold",
								children: "Nivel 4 · Evaluaciones"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-sm text-muted-foreground",
								children: "Define los tipos de pregunta y las actividades calificables con su peso en la nota final."
							})] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mb-1.5 text-xs font-medium text-muted-foreground",
								children: "Tipos de pregunta"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "flex flex-wrap gap-2",
								children: questionTypeOptions.map((q) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Chip, {
									active: questionTypes.includes(q),
									onClick: () => toggleQuestion(q),
									children: q
								}, q))
							})] }),
							acts.map((a, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "rounded-lg border border-border bg-surface p-4",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "mb-3 flex items-center justify-between",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
											className: "text-sm font-bold",
											children: ["Actividad ", i + 1]
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
											"aria-label": "Quitar actividad",
											onClick: () => setActs((x) => x.filter((_, j) => j !== i)),
											className: "rounded p-1 text-muted-foreground hover:bg-muted",
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "size-4" })
										})]
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "mb-1.5 text-xs font-medium text-muted-foreground",
										children: "Tipo"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "flex flex-wrap gap-2",
										children: activityTypes.map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Chip, {
											active: a.tipo === t,
											onClick: () => updAct(i, { tipo: t }),
											children: t
										}, t))
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "mt-4 grid gap-3 sm:max-w-sm",
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
											className: "block",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
												className: "mb-1.5 block text-xs font-medium text-muted-foreground",
												children: "Porcentaje de la nota (vacío = lo define la IA)"
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
												type: "number",
												min: 0,
												max: 100,
												value: a.porcentaje ?? "",
												onChange: (e) => updAct(i, { porcentaje: e.target.value === "" ? null : Number(e.target.value) }),
												className: "h-10 w-full rounded-lg border border-input bg-surface px-3 text-sm"
											})]
										})
									})
								]
							}, i)),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex flex-wrap items-center justify-between gap-3",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
									variant: "secondary",
									onClick: () => setActs((x) => [...x, {
										tipo: "Examen",
										cantidad: 1,
										porcentaje: null
									}]),
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Plus, { className: "size-4" }), "Agregar actividad"]
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: cn("text-xs font-semibold", evalErrors.length ? "text-destructive" : "text-muted-foreground"),
									children: [
										"Suma: ",
										pctSum,
										"% · Total actividades: ",
										config.evaluacion.total_actividades ?? 0
									]
								})]
							}),
							evalErrors.map((e) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-xs text-destructive",
								children: e
							}, e)),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "rounded-lg border border-border bg-muted/50 p-4",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
									className: "mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground",
									children: "Generado automáticamente"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Auto, { items: ["Preguntas y ejercicios", "Retroalimentación"] })]
							})
						]
					}),
					step === 4 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "space-y-5",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
								className: "font-bold",
								children: "Revisión y envío"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-sm text-muted-foreground",
								children: "La asignación de modelos de IA para cada tarea la gestiona el orquestador del backend."
							})] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(V2Mark, {
								label: "Versión 2.0",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "rounded-lg border border-info/20 bg-primary-soft p-4 text-sm text-muted-foreground",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
										className: "font-medium text-foreground",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldCheck, { className: "mr-2 inline size-4 text-primary" }), "Filtro transversal de restricciones"]
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "mt-3 flex flex-wrap gap-1.5",
										children: restrictions.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "rounded-full bg-surface px-2.5 py-1 text-xs",
											children: r
										}, r))
									})]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("details", {
								className: "rounded-lg border border-border bg-surface p-4 text-sm",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("summary", {
									className: "cursor-pointer font-medium",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(FileText, { className: "mr-2 inline size-4 text-primary" }), "Vista previa del JSON para el backend"]
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
									className: "mt-3 max-h-80 overflow-auto rounded-md bg-muted p-3 text-xs",
									children: JSON.stringify(config, null, 2)
								})]
							}),
							errors.map((e) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-xs text-destructive",
								children: e
							}, e))
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-7 flex flex-wrap justify-between gap-2 border-t border-border pt-5",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "secondary",
							disabled: step === 1,
							onClick: () => setStep((s) => s - 1),
							children: "Anterior"
						}), step < 4 ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							disabled: !stepValid[step - 1],
							onClick: () => setStep((s) => s + 1),
							children: ["Continuar", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronRight, { className: "size-4" })]
						}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							disabled: !stepValid[3],
							onClick: () => void generate(),
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Sparkles, { className: "size-4" }), "Generar curso con IA"]
						})]
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
				className: "mt-4 flex items-center gap-2 text-xs text-muted-foreground",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleAlert, { className: "size-4" }), "SICCIA no genera formación médica, técnica especializada o de alto riesgo."]
			})
		]
	});
}
function Result({ go, job, config }) {
	const [busy, setBusy] = (0, import_react.useState)(null);
	const [error, setError] = (0, import_react.useState)(null);
	if (!job || !config) return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		className: "glass-panel mx-auto max-w-xl rounded-xl p-8 text-center",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "text-sm text-muted-foreground",
			children: "No hay un curso generado en esta sesión."
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
			className: "mt-4",
			onClick: () => go("generator"),
			children: "Generar curso"
		})]
	});
	const run = async (key, fn) => {
		setBusy(key);
		setError(null);
		try {
			await fn();
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error al descargar");
		} finally {
			setBusy(null);
		}
	};
	const pdfs = job.archivos.filter((a) => a.nombre.endsWith(".pdf"));
	const archivosDescargables = pdfs.length ? pdfs.map((pdf) => ({
		...pdf,
		via: job.archivos.find((a) => a.nombre === pdf.nombre.replace(/\.pdf$/, ".md"))?.via ?? pdf.via
	})) : job.archivos;
	const byVia = Object.keys(viaLabels).map((v) => ({
		via: v,
		files: archivosDescargables.filter((a) => a.via === v)
	}));
	const otros = archivosDescargables.filter((a) => !(a.via in viaLabels));
	if (otros.length) byVia.push({
		via: "otros",
		files: otros
	});
	const ok = job.estado === "completado";
	const c = config.contenido;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-5",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
			className: "glass-panel rounded-xl p-5",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid gap-4 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: cn("inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold", ok ? "bg-success-soft text-success" : "bg-warning-soft text-warning"),
						children: [ok ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "size-3" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleAlert, { className: "size-3" }), estadoLabels[job.estado]]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "mt-3 text-xl font-bold",
						children: config.datos.tema
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 text-sm text-muted-foreground",
						children: [
							config.datos.duracion_estimada,
							c.modulos_modo === "manual" ? `${c.modulos.length} módulos` : "Módulos automáticos",
							config.datos.metodologia
						].filter(Boolean).join(" · ")
					})
				] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					disabled: !pdfs.length || busy !== null,
					title: pdfs.length ? void 0 : "No hay PDF para descargar",
					onClick: () => run("zip", () => descargarZipPdf(job.id)),
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Download, { className: "size-4" }), busy === "zip" ? "Descargando..." : `Descargar PDF (.zip)`]
				})]
			}), error && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3 text-xs text-destructive",
				children: error
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "glass-panel overflow-hidden rounded-xl",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "border-b border-border p-5",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
							className: "font-bold",
							children: "Materiales generados"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "text-sm text-muted-foreground",
							children: [archivosDescargables.length, " archivo(s) PDF listos para descargar."]
						})]
					}),
					byVia.filter((g) => g.files.length).map((g) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "border-b border-border p-4 last:border-0",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground",
							children: viaLabels[g.via] ?? "Otros"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "space-y-2",
							children: g.files.map((f) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 rounded-lg border border-border bg-surface p-3",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "grid size-8 place-items-center rounded-md bg-primary-soft text-primary",
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(FileText, { className: "size-4" })
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "min-w-0",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
											className: "truncate text-sm",
											children: f.nombre
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
											className: "text-xs text-muted-foreground",
											children: [(f.tamano_bytes / 1024).toFixed(1), " KB"]
										})]
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
										size: "sm",
										variant: "secondary",
										disabled: busy !== null,
										onClick: () => run(f.nombre, () => descargarArchivo(job.id, f.nombre)),
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Download, { className: "size-4" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "hidden sm:inline",
											children: busy === f.nombre ? "..." : "Descargar"
										})]
									})
								]
							}, f.nombre))
						})]
					}, g.via)),
					!job.archivos.length && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "p-5 text-sm text-muted-foreground",
						children: "El trabajo no generó archivos."
					})
				]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("aside", {
				className: "space-y-4",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
						className: "glass-panel rounded-xl p-5",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
								className: "font-bold",
								children: "Vías de trabajo"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "mt-4 space-y-3 text-sm",
								children: Object.entries(job.vias).map(([v, s]) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-start justify-between gap-3",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "text-muted-foreground",
										children: viaLabels[v] ?? v
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("b", {
										className: cn("text-right", viaCompletada(s) ? "text-success" : s === "omitida" || s === "pendiente" ? "text-muted-foreground" : s === "en_curso" ? "text-primary" : "text-destructive"),
										children: viaStatusLabel(s)
									})]
								}, v))
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "mt-4 text-xs text-muted-foreground",
								children: [
									"Trabajo ",
									job.id.slice(0, 8),
									" · ",
									new Date(job.creado_en).toLocaleString("es-CO")
								]
							})
						]
					}),
					job.error && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
						className: "rounded-xl border border-warning/25 bg-warning-soft p-5",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleAlert, { className: "size-5 text-warning" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 text-xs text-muted-foreground",
							children: job.error
						})]
					}),
					!!job.advertencias.length && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
						className: "rounded-xl border border-warning/25 bg-warning-soft p-5",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
							className: "font-semibold",
							children: "Advertencias"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
							className: "mt-2 list-disc space-y-1 pl-5 text-xs text-muted-foreground",
							children: job.advertencias.map((advertencia, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: advertencia }, `${i}-${advertencia}`))
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						className: "w-full",
						variant: "secondary",
						onClick: () => go("generator"),
						children: "Generar otro curso"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						className: "w-full",
						variant: "ghost",
						onClick: () => go("dashboard"),
						children: "Volver al panel"
					})
				]
			})]
		})]
	});
}
function SettingsView({ user }) {
	const [saved, setSaved] = (0, import_react.useState)(false);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		className: "glass-panel mx-auto max-w-2xl rounded-xl p-5 sm:p-7",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "text-xl font-bold",
				children: "Información personal"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-1 text-sm text-muted-foreground",
				children: "Datos del docente que se muestran en SICCIA."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-6 space-y-5",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
						label: "Nombre visible",
						defaultValue: displayName(user)
					}),
					user.email && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "block",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "mb-1.5 block text-sm font-medium",
							children: "Correo electrónico"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							readOnly: true,
							value: user.email,
							className: "h-11 w-full rounded-lg border border-input bg-muted px-3 text-sm text-muted-foreground"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "block",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "mb-1.5 block text-sm font-medium",
							children: "Institución"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							className: "h-11 w-full rounded-lg border border-input bg-surface px-3 text-sm",
							defaultValue: "Institución Educativa San Rafael"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						onClick: () => setSaved(true),
						children: saved ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "size-4" }), "Cambios guardados"] }) : "Guardar cambios"
					})
				]
			})
		]
	});
}
//#endregion
export { Index as component };
