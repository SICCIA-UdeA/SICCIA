async def _procesar(self, trabajo: Trabajo, config: Configurador) -> None:
        try:
            trabajo.estado = EstadoTrabajo.PLANIFICANDO
            plan = await Planificador(self._fabrica("planificador")).completar(config)
            madre = construir_plantilla_madre(plan)
            self._guardar_interno(trabajo, "configurador.json", config.model_dump_json(indent=2))
            self._guardar_interno(trabajo, "plan_curso.json", plan.model_dump_json(indent=2))
            self._guardar_interno(trabajo, "plantilla_madre.md", madre)

            trabajo.estado = EstadoTrabajo.EJECUTANDO
            trabajo.vias = {v.rol: "pendiente" for v in self._crear_vias()}
            
            # --- FASE 1 (Contenido y Programa en paralelo) ---
            log.info(f"[{trabajo.id}] Iniciando Fase 1: Programa y Contenido")
            vias_fase_1 = [
                ViaPrograma(self._fabrica("programa")),
                ViaContenido(self._fabrica("contenido"))
            ]
            for v in vias_fase_1:
                trabajo.vias[v.rol] = "en_curso"
                
            resultados_fase_1 = await asyncio.gather(
                *(self._correr_via(trabajo, v, madre, config, plan) for v in vias_fase_1)
            )

            # --- RESCATE DEL TEXTO PARA FASE 2 ---
            if "contenido_curso.md" in trabajo.archivos:
                texto_contenido = trabajo.archivos["contenido_curso.md"].contenido
            else:
                texto_contenido = "ADVERTENCIA CRÍTICA: EL CONTENIDO NO SE GENERÓ DEBIDO A UN FALLO. NOTIFIQUE ESTE ERROR."

            madre_fase_2 = (
                madre + 
                "\n\n## ATENCIÓN: CONTENIDO REAL GENERADO\n"
                "Básate ESTRICTAMENTE en esta teoría para tu tarea. "
                "No evalúes ni verifiques conceptos que no estén aquí:\n\n"
                f"{texto_contenido}"
            )

            # --- FASE 2 (Evaluación y Verificación en paralelo) ---
            log.info(f"[{trabajo.id}] Iniciando Fase 2: Evaluación y Verificación")
            vias_fase_2 = [ViaEvaluacion(self._fabrica("evaluacion"))]
            if ViaVerificacion:
                vias_fase_2.append(ViaVerificacion(self._fabrica("verificacion")))
                
            for v in vias_fase_2:
                trabajo.vias[v.rol] = "en_curso"
                
            resultados_fase_2 = await asyncio.gather(
                *(self._correr_via(trabajo, v, madre_fase_2, config, plan) for v in vias_fase_2)
            )

            # --- COMPROBACIÓN FINAL Y CREACIÓN DE PDF CORREGIDA ---
            exitosas = sum(resultados_fase_1) + sum(resultados_fase_2)
            total_vias = len(vias_fase_1) + len(vias_fase_2)
            
            if exitosas > 0:
                # El estado refleja fielmente si todas las vías pasaron o si algunas fallaron
                if exitosas == total_vias:
                    trabajo.estado = EstadoTrabajo.COMPLETADO
                else:
                    trabajo.estado = EstadoTrabajo.COMPLETADO_CON_ERRORES
                
                try:
                    from .exportador_pdf import procesar_imagenes_y_pdf
                    # Solo le pasamos a la librería los archivos que sí se completaron exitosamente
                    procesar_imagenes_y_pdf(trabajo.dir_resultados, trabajo.archivos)
                    log.info(f"[{trabajo.id}] Procesados los PDFs de las {exitosas} vías exitosas.")
                except ImportError:
                    pass
                    
            else:
                # Si fallan absolutamente todas las vías, abortamos totalmente
                trabajo.estado = EstadoTrabajo.ERROR
                trabajo.error = "Ninguna vía de trabajo logró completarse (todas fallaron tras los reintentos)."
                
        except Exception as exc:  # noqa: BLE001
            log.exception("Trabajo %s falló", trabajo.id)
            trabajo.estado = EstadoTrabajo.ERROR
            trabajo.error = str(exc)