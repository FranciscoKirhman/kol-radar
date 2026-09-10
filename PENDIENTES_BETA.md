# Pendientes conocidos de la beta

Lo que se dejó explícitamente sin resolver para llegar al lanzamiento, con la razón. Ninguno de
estos es un descubrimiento posterior: todos se detectaron antes de publicar y se decidió
diferirlos. Está acá para que la próxima iteración no empiece a buscarlos de cero.

Fecha de corte: 2026-09-10.

## Datos

- **253 sedes sin resolver.** Son textos de sede que ClinicalTrials.gov declara en Chile y que
  ningún alias documentado liga todavía a una institución canónica: "Instituto Oncologico",
  "Health & Care SPA", "Rey y O'Reilly Limitada", entre otros. **No son evidencia negativa**: el
  centro existe y la fuente lo nombra. Están en
  `data/pending/preintegracion-clinicaltrials-2026-09-09/sedes_sin_resolver.json` y, cuando
  pertenecen a un ensayo, también dentro de ese ensayo en `sedes_pendientes_resolucion`.
- **264 ensayos sin institución canónica.** Entraron igual, con su NCT y su URL, porque la fuente
  sí declara un sitio en Chile. Quedan sin vínculo, así que no aparecen en el grafo (grado 0)
  pero sí en la lista, la búsqueda y su ficha.
- **7 personas candidatas en cola por posible fusión.** ClinicalTrials.gov las nombra con un rol
  individual y coinciden con una ficha ya existente: "Christian Caglevic Medina" contra
  "Christian Caglevic", "Hector Gonzalo Galindo Aranibar" contra "Héctor Galindo". **No se
  fusionaron ni se duplicaron**: fusionar es una decisión humana. Están en
  `personas_candidatas.json` con `decision_humana` vacío.
- **48 candidatos como "posible coincidencia" y 60 no utilizables** (`Study Coordinator`,
  contactos corporativos, códigos de sitio). Ninguno creó ficha.
- **Dos fusiones de identidad abiertas** desde antes: Aguayo y Díaz Patiño, en `DECISIONS.md` §5.
- **817 de 818 hechos siguen en `pendiente`.** El único `confirmado` es el ORCID de Claudio Silva
  Fuente-Alba, aprobado por revisión humana en su momento. Nada de la expansión fue corroborado
  por una persona.
- **El área de un ensayo se asigna por la condición que declara la fuente**, y ante empate gana
  el área con menos ensayos. Es una heurística, no una clasificación clínica.

## Interfaz

- **El mapa dibuja como máximo 400 nodos.** El layout es O(n²) y con 717 nodos bloqueaba el hilo
  principal 7,6 segundos — medido. Se acotó a los 400 de mayor grado y el aviso del mapa dice
  cuántos quedaron fuera. La solución correcta es un quadtree (Barnes-Hut); se difirió por
  riesgo, no por falta de diagnóstico.
- **Las iteraciones de la simulación bajan de 300 a 45 cuando hay más de 300 nodos.** Es lo que
  llevó el peor caso de 7,6 s a 1,1 s. Con un quadtree se podrían recuperar las 300.
- **La vista "Ecosistema completo" es una maraña.** Con 400 nodos densamente conectados, el
  grafo se ve como una bola. La vista por defecto ("Quién trabaja dónde") sí es legible. Falta
  una estrategia de agregación para la vista completa.
- **Nombres tal como los escribe la fuente.** Solo se normalizó la caja de las mayúsculas
  ("Myriam CAMPBELL BULL" → "Myriam Campbell Bull"). No se corrigen tildes ni abreviaturas.

## Modelo de puntaje

Sin tocar, deliberadamente: no se cambiaron pesos, umbrales, tope de red ni la heurística de
guías, porque calibrarlos sin haber validado con un MSL sería mover números hasta que se parezcan
a nuestra intuición. El diagnóstico ya está hecho:

- La red aporta más de la mitad del puntaje a la mayoría de las personas.
- Cinco perfiles llegan a "Prioridad alta" con un solo hecho clasificado como guía o consenso.
- La clasificación de guía/consenso se deriva del texto, no de una revisión humana.
- Los topes por dimensión siguen sin ejercerse: nadie supera cinco recursos únicos.

## Proceso

- **Etapa 3** (revisión humana de 30 fichas): preparada, no ejecutada.
- **Etapa 6** (validación con un MSL): no ejecutada. **Nada acá está validado con un MSL.**
- **Canal privado de corrección**: sigue sin definirse. El botón "Reportar un error" va a los
  issues del repositorio, que son **públicos** — sirve para que un tester reporte un dato malo,
  no para que un profesional pida que se retire su ficha sin exponerse. El pie de página lo dice.
