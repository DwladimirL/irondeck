# Cómo funciona IronDeck

Esta guía explica las piezas de IronDeck, el orquestador de Claude Code para Windows, y cómo se mueve un trabajo de principio a fin. IronDeck está en desarrollo: lo que cuenta aquí ya existe en el código, y los detalles pueden cambiar antes del lanzamiento.

[English version](guide.md) · [Volver al inicio](../README.es.md)

## Para quién es

Para quien ya trabaja con Claude Code y quiere delegar trabajos largos: construir una parte de una app, afinar una skill, revisar un proyecto. Tú decides qué se hace y revisas lo terminado. IronDeck se encarga de lanzar las tareas, esperar, reintentar, cuidar tu plan y avisarte cuando te necesita.

## Las piezas

| Pieza | Qué es |
|---|---|
| **Proyecto** | Un repositorio en el que trabajas, con su ventana propia en IronDeck. |
| **Flujo** | Los pasos de un trabajo, en orden. Por ejemplo: investigar, diseñar, construir, revisar. |
| **Paso** | Una parte del flujo, con su modelo (Sonnet, Opus…), su esfuerzo, sus permisos y el contexto que puede leer. |
| **Tarea** | Una ejecución de Claude Code para un paso. Cada tarea corre en su propia copia del proyecto, así no pisa tu trabajo. |
| **Bandeja** | Donde esperan las decisiones que te tocan: fusionar un cambio, pasar el tope de la semana, qué hacer tras un segundo fallo. |
| **Biblioteca** | Tus skills y plantillas, con todas sus versiones. |
| **Evaluación** | Una comparación entre dos versiones de una skill sobre los mismos casos. |
| **Guardia de cobro** | El control que decide qué se puede cobrar: solo tu plan, o también el uso extra de tu cuenta hasta tu tope. |

## Un trabajo de principio a fin

1. **Eliges un proyecto y un flujo.** Puedes partir de una plantilla; se adapta a tu proyecto.
2. **IronDeck lanza la primera tarea.** Prepara una copia de trabajo y corre Claude Code con el modelo y el esfuerzo de ese paso. Puede correr hasta cuatro tareas a la vez. Los pasos corren en orden; que cada paso reciba el resultado del anterior llega en la fase actual.
3. **Si algo falla, reintenta.** Falla una tarea que termina con error o con la entrega a medias. El segundo intento va con un modelo mayor, si lo hay; un permiso negado la detiene sin reintentar. Si vuelve a fallar, la decisión pasa a tu bandeja.
4. **Al terminar un paso con cambios, te propone fusionarlos.** Nada llega a tu rama principal sin tu sí.
5. **Si llegas al límite de tu plan, pausa.** No cuenta como fallo: retoma sola después del reinicio. Si permitiste el uso extra, sigue sin pausar hasta tu tope.
6. **Si cierras IronDeck o se apaga la PC, no pierdes el avance.** Al abrirlo, repite el paso que quedó a medias; lo terminado no se repite.

## Cómo controla el gasto

- **Tú eliges cómo se paga.** Por defecto, solo con tu plan: antes de lanzar comprueba con qué cuenta va a correr Claude Code, y mientras la tarea corre la corta en cuanto ve una clave de API o Claude Code informa un uso que se cobraría aparte. Si prefieres que no se detenga, podrás permitir el uso extra de tu cuenta hasta un tope en dinero; ese modo llega antes del lanzamiento. IronDeck no usa claves de API.
- **Te muestra tu uso.** El límite de 5 horas y el de la semana, con las mismas cifras que ves en claude.ai. Los lee de los avisos de límite que el propio Claude Code emite mientras trabaja.
- **Respeta tu tope.** Puedes fijar un tope para la semana. Al llegar, pregunta antes de seguir.
- **Ninguna tarea corre para siempre.** Cada una tiene un límite de 6 horas.

## La biblioteca y las versiones

- **Importa tus paquetes `.skill`** sin perder las versiones anteriores.
- **El número de versión nunca baja.** Restaurar una versión vieja crea una nueva, con una nota de cuál restauró.
- **Las evaluaciones A/B** corren cada caso tres veces con cada versión, porque la respuesta de un modelo cambia entre corridas, y Opus juzga los resultados.
- **Antes de empaquetar**, IronDeck revisa la skill con las reglas del validador oficial. Solo exporta lo que pasa.

## Lo que vas a necesitar

Lista provisional; la final sale con la primera versión.

- Windows, nativo (sin WSL).
- Claude Code instalado, con la sesión de tu cuenta de Claude iniciada.
- Un plan de Claude que incluya Claude Code: Pro o Max, o un plan Team o Enterprise. El uso extra es opcional.
- Git y Node.js.

## Lo que IronDeck no hace

- No guarda tu contraseña ni manda tu sesión a ningún servidor.
- No fusiona nada en tu proyecto sin tu aprobación. Lo que publiquen las tareas depende de los permisos que les des.
- No corre en la nube: todo pasa en tu PC.

---

¿Más preguntas? Están en el [sitio](https://dwladimirl.github.io/irondeck/#preguntas).

IronDeck es un proyecto independiente y no está afiliado a Anthropic. Claude y Claude Code son marcas de Anthropic, PBC.
