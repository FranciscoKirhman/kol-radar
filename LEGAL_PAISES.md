# Evaluación preliminar por país

No es asesoría legal. Esta propuesta requiere aprobación de Francisco y revisión jurídica local antes de activar nuevos países. El país de afiliación es la barrera técnica solicitada; no determina por sí solo todas las leyes aplicables.

Los estados son propuestas técnicas conservadoras para este producto y requieren decisión de Francisco; solo CL conserva la aprobación indicada por él. «Blocked» también puede indicar evidencia insuficiente, no necesariamente prohibición absoluta. La afiliación es una barrera de producto: por sí sola no determina qué leyes se aplican. Debe revisarse también establecimiento del responsable, residencia, alcance territorial y ubicación del tratamiento. Las recomendaciones y evaluaciones de certeza se marcan [NO VERIFICADO] porque son juicio de implementación, no hechos establecidos por una autoridad.

No se verificó una excepción general por esfuerzo desproporcionado fuera de los casos expresamente descritos. No trasladar la excepción RGPD automáticamente a otros países. `plazo_bloqueo: inmediato` es una política del producto, no un plazo legal universal. Conservar además unidad (hábiles/corridos), tipo de derecho, disparador y fuente; un entero de días no basta para calcular vencimientos legales. Mientras falte un plazo verificado, usar `null` y derivación humana; nunca inventar 30 días por defecto.

## Chile — CL

- [VERIFICADO: https://www.bcn.cl/leychile/navegar?idNorma=141599&idVersion=2012-02-17] Ley 19.628, arts. 4, 6, 12 y 16: excepción limitada para ciertos listados profesionales de fuentes públicas; acceso, corrección, cancelación y bloqueo; dos días **hábiles** sin pronunciamiento habilitan reclamación judicial. El art. 22 registra bancos de organismos públicos. El texto no ofrece una autorización general para todo perfil o puntaje derivado.
- [NO VERIFICADO] Base plausible: excepción del art. 4 para antecedentes profesionales, pendiente revisar si el perfil enriquecido y puntaje permanecen dentro de ese supuesto. Aviso indirecto equivalente al RGPD, excepción por esfuerzo desproporcionado, representante local y encuadre concreto de alojamiento internacional: no determinados para este proyecto.
- [VERIFICADO: https://www.bcn.cl/leychile/navegar?idNorma=1209272] Ley 21.719 modifica bases, derechos y transferencias, con entrada diferida de las modificaciones el primer día del mes 24 posterior a su publicación (13 diciembre 2024): 1 diciembre 2026. No aplicar anticipadamente sus plazos como si fueran los actuales.
- [NO VERIFICADO] Propuesta `allowed_with_conditions`; aprobación `allowed` exclusivamente por instrucción del usuario. Certeza media. Respuesta operativa máxima: 2 días, unidad hábiles; bloqueo inmediato como política. Revisión legal chilena antes del 1 diciembre 2026 y antes de ampliar categorías de perfil.

## Argentina — AR

- [VERIFICADO: https://www.argentina.gob.ar/normativa/nacional/64790/actualizacion] Ley 25.326, arts. 3–6, 14, 16 y 21: excepción al consentimiento para fuentes de acceso público irrestricto, finalidad compatible y calidad; información previa; acceso en 10 días corridos y rectificación/supresión en 5 días hábiles. Regula inscripción de bases y bloqueo o anotación mientras se verifica una reclamación. No confundir excepción al consentimiento con ausencia de otros deberes.
- [VERIFICADO: https://www.argentina.gob.ar/transferencias-internacionales] AAIP exige examinar adecuación del destino; permite excepciones y cláusulas modelo para transferencias a destinos no adecuados. Chile no figura en la lista consultada.
- [VERIFICADO: https://www.argentina.gob.ar/aaip/datospersonales/responsables/obligaciones] AAIP documenta obligaciones de inscripción y mecanismos de transferencia.
- [NO VERIFICADO] Propuesta `allowed_with_conditions`, certeza media: confirmar encuadre de fuentes científicas, puntajes, aviso para recolección indirecta, inscripción del responsable extranjero y mecanismo de publicación internacional. No se verificó excepción general de esfuerzo desproporcionado ni requisito de representante para esta operación. Requiere revisión local. Respuesta por derecho: acceso 10 corridos; rectificación/supresión 5 hábiles; bloqueo inmediato como política.

## Brasil — BR

- [VERIFICADO: https://planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm] LGPD, arts. 7 IX, 9–10, 18–19, 33 y 41: interés legítimo sujeto a derechos y expectativas; transparencia; oposición por incumplimiento cuando se prescinde del consentimiento; acceso simplificado inmediato o completo hasta 15 días. Transferencias deben encajar en mecanismos legales; prevé encargado. Los 15 días no son un plazo general de supresión ni oposición.
- [VERIFICADO: https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia_legitimo_interesse.pdf/@@display-file/file] Guía ANPD exige evaluar finalidad, necesidad, balance y salvaguardas; interés legítimo no ampara datos sensibles.
- [NO VERIFICADO] Propuesta `allowed_with_conditions`, certeza media: evaluación documentada del interés legítimo para perfiles profesionales no sensibles, aviso y canal de derechos, confirmación del régimen de encargado y transferencias. No se verificó excepción general de aviso indirecto por esfuerzo desproporcionado; tampoco exención concreta de encargado/registro para KOL Radar. Abogado local antes de activar. `plazo_respuesta_dias: 15` solo acceso completo; para otros derechos, `null` hasta completar reglas. Bloqueo inmediato como política.

## México — MX

- [VERIFICADO: https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf] Ley federal de 2025, texto reformado 14 noviembre 2025: arts. 2 VIII/X, 9, 14–17, 26, 29 y 31. Excepción de consentimiento para fuentes públicas con definición legal restringida; aviso; oposición; persona/departamento de datos; decisión ARCO en 20 días hábiles y ejecución favorable en 15 siguientes. Art. 17 prevé medidas compensatorias cuando informar directamente sea imposible o desproporcionado, sujetas al reglamento.
- [VERIFICADO: https://www.ordenjuridico.gob.mx/Documentos/Federal/html/wo125102.html] Segundo portal oficial del texto de 2025: transferencias nacionales/extranjeras sujetas a aviso, obligaciones del receptor y consentimiento o excepción (arts. 35–36). Es corroboración del mismo instrumento, no un dictamen independiente.
- [NO VERIFICADO] Propuesta `allowed_with_conditions`, certeza media: confirmar que CT.gov/PubMed/OpenAlex encajan como fuente pública legal, aviso/medidas compensatorias aplicables, transferencias y régimen territorial. No se verificó representante extranjero ni registro aplicable. Requiere abogado local y revisión del reglamento vigente antes de activar. Respuesta 20 hábiles; bloqueo inmediato como política.

## Colombia — CO

- [NO VERIFICADO] Las búsquedas localizaron Ley 1581/2012 y Decreto 1377/2013, pero sus páginas oficiales devolvieron errores al abrir. No se computan como fuentes verificadas. Tampoco se pudo abrir contenido íntegro en SIC sobre finalidad y política de tratamiento.
- [NO VERIFICADO] Base plausible por investigar: datos de naturaleza pública bajo Ley 1581; no basta accesibilidad en internet. Aviso indirecto/excepciones, oposición y plazos, representante/registro RNBD, transferencias y alcance territorial: pendientes de comprobación con textos abiertos.
- [NO VERIFICADO] Propuesta `blocked`, certeza baja, `plazo_respuesta_dias: null`; bloqueo inmediato como política. Revisión local obligatoria antes de activar. Cero fuentes sustantivas abiertas válidas en esta investigación.
- URLs intentadas, **no incluir en `fuentes_legales` verificadas**: https://sedeelectronica.sic.gov.co/transparencia/normativa/ley-estatutaria-1581-de-2012 ; https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php/norma.php?i=49981 ; https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php/norma.php?i=53646

## Perú — PE

- [VERIFICADO: https://leyes.congreso.gob.pe/DetLeyNume_1p.aspx?xNorma=6&xNumero=29733&xTipoNorma=0] El Congreso identifica la Ley 29733 de protección de datos personales, publicada 3 julio 2011.
- [VERIFICADO: https://leyes.congreso.gob.pe/documentos/leyes/29733.pdf] Se abrió el PDF oficial (8 páginas); extracción textual no disponible. Esta apertura acredita disponibilidad, no se usa para afirmar artículos no leídos.
- [NO VERIFICADO] No se logró verificar íntegramente el reglamento vigente 016-2024-JUS (errores en Congreso, Gob.pe y CDN oficial). Base para perfil público, información indirecta/excepciones, oposición/plazos, registro, representante y transferencias quedan pendientes. Dos URL del mismo instrumento no resuelven esta carencia sustantiva.
- [NO VERIFICADO] Propuesta `blocked`, certeza baja, `plazo_respuesta_dias: null`; bloqueo inmediato como política. Requiere revisar ley y reglamento vigente con abogado local antes de activar.

## Uruguay — UY

- [VERIFICADO: https://www.impo.com.uy/bases/leyes/18331-2008] Ley 18.331, arts. 9, 13–16 y 23: excepción de consentimiento para fuentes públicas; información sobre tratamiento indirecto dentro de 5 días hábiles de recibida solicitud; acceso y rectificación/supresión en 5 hábiles. Regula impugnación de valoraciones automatizadas y limita transferencias a destinos sin protección adecuada, con excepciones. No convertir la excepción de consentimiento en permiso general para puntajes.
- [VERIFICADO: https://www.gub.uy/unidad-reguladora-control-datos-personales/comunicacion/publicaciones/preguntas-frecuentes/preguntas-frecuentes/sobre-inscripcion-base-datos] URCDP explica obligación de inscripción de bases, también manuales.
- [NO VERIFICADO] Propuesta `allowed_with_conditions`, certeza media: inscripción, evaluación del puntaje y transferencias; confirmar representante/alcance extraterritorial. No se verificó una excepción general de aviso por esfuerzo desproporcionado. Revisión local antes de activar. Respuesta 5 hábiles; bloqueo inmediato como política.

## Costa Rica — CR

- [VERIFICADO: https://www.micitt.go.cr/sites/default/files/marco_juridico_legal/08.%20Ley%20n.%C2%B0%208968%20Ley%20de%20Protecci%C3%B3n%20de%20la%20Persona%20frente%20al%20tratamiento%20de%20sus%20datos%20personales..pdf] Ley 8968, arts. 3, 5, 7, 14 y 21: excepción para datos de acceso irrestricto, definidos según leyes especiales y finalidad; deber de informar al solicitar datos; acceso/rectificación y resolución en 5 hábiles; transferencia requiere autorización expresa válida; bases destinadas a difusión/distribución/comercialización se inscriben.
- [VERIFICADO: https://formatos.inamu.go.cr/SIDOC/DOCS/ley_8968.pdf] Segunda publicación oficial de la misma ley. No equivale a una segunda interpretación.
- [NO VERIFICADO] Propuesta `blocked`, certeza media: no se acreditó que difusión mundial de perfiles/puntajes sin autorización satisfaga reglas de transferencia ni la definición de acceso irrestricto. Aviso indirecto y excepción por esfuerzo, representante y reglamento aplicable requieren abogado local antes de activar. Respuesta 5 hábiles para derechos verificados; bloqueo inmediato como política.

## Estados Unidos — US

- [VERIFICADO: https://www.oag.ca.gov/privacy/ccpa?version=published] California: CCPA excluye determinada información pública y concede acceso/corrección/supresión a sujetos cubiertos, con respuesta ordinaria en 45 días corridos. Exenciones laborales/B2B expiraron al final de 2022. Información profesional no queda automáticamente exenta.
- [VERIFICADO: https://www.cppa.ca.gov/data_brokers/] CPPA describe registro de data brokers y obligación desde agosto 2026 de consultar DROP al menos cada 45 días y procesar solicitudes.
- [NO VERIFICADO] Propuesta `blocked`, certeza baja para alcance nacional: estas dos fuentes verifican California, no los otros estados ni reglas federales/sectoriales. No se establece base legal nacional, excepción de aviso indirecto, representante, registro o transferencias para todo EE. UU. Afiliación US carece de estado: insuficiente para activación jurídica uniforme. Requiere evaluación multiestatal local, modelo de negocio y umbrales. `plazo_respuesta_dias: null` nacional; 45 corridos es solo ejemplo CCPA, no regla universal. Bloqueo inmediato como política.

## Canadá — CA

- [VERIFICADO: https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/pipeda-compliance-help/pipeda-interpretation-bulletins/interpretations_06_pai/] OPC: la excepción de información pública bajo PIPEDA cubre categorías reglamentadas; registros/directorios requieren compatibilidad con su finalidad original.
- [VERIFICADO: https://www.priv.gc.ca/en/opc-actions-and-decisions/investigations/investigations-into-businesses/2019/pipeda-2019-006/] OPC consideró insuficiente que datos estuvieran visibles en una web para justificar su incorporación a un directorio sin consentimiento.
- [VERIFICADO: https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/p_principle/principles/p_access/] Acceso bajo PIPEDA: respuesta hasta 30 días, con prórroga limitada y notificación.
- [VERIFICADO: https://www.priv.gc.ca/en/privacy-topics/airports-and-borders/gl_dab_090127/?wbdisable=true] Transferencias para procesamiento requieren protección comparable y transparencia; la guía no resuelve regímenes provinciales ni una divulgación pública internacional.
- [NO VERIFICADO] Propuesta `blocked`, certeza media: no se validó compatibilidad de perfil/puntaje con finalidad de cada fuente ni regímenes provinciales. Aviso indirecto/excepción por esfuerzo, oposición/supresión, representante/registro: evaluación local pendiente. Respuesta acceso 30 corridos; otros derechos sin plazo verificado. Bloqueo inmediato como política.

## Tabla sugerida para configuración

| ISO2 | Propuesta | Aprobado | Certeza | Días de respuesta verificables | Unidad/alcance |
|---|---|---|---|---:|---|
| CL | allowed_with_conditions | allowed | media | 2 | hábiles, pronunciamiento art.16 régimen actual |
| AR | allowed_with_conditions | null | media | 5 | hábiles rectificación/supresión; acceso 10 corridos |
| BR | allowed_with_conditions | null | media | 15 | acceso completo; otros derechos no determinado |
| MX | allowed_with_conditions | null | media | 20 | hábiles decisión; ejecución favorable 15 siguientes |
| CO | blocked | null | baja | null | sin texto sustantivo abierto |
| PE | blocked | null | baja | null | reglamento no verificado |
| UY | allowed_with_conditions | null | media | 5 | hábiles |
| CR | blocked | null | media | 5 | hábiles |
| US | blocked | null | baja | null | no existe verificación nacional completa |
| CA | blocked | null | media | 30 | corridos acceso PIPEDA; provincias pendientes |

Todas las filas: bloqueo inmediato por política de producto y revisión legal local antes de activación o ampliación. Para CO `fuentes_legales: []`; PE puede conservar las dos URL abiertas con las limitaciones expresas anteriores. No incluir intentos fallidos como evidencia verificada.

Revisión: 2026-10-06. Es una propuesta conservadora para revisión humana; ningún país de este documento debe recibir `estado_aprobado` distinto de `null`.

`blocked` puede significar evidencia insuficiente para habilitar este producto; no afirma que toda forma de tratamiento esté prohibida en esa jurisdicción. Las páginas con captcha, error o sin texto no cuentan como fuentes verificadas. Las propuestas `allowed_with_conditions` tampoco acreditan que las condiciones se hayan cumplido. En todos los casos se requiere abogado local antes de activar perfiles públicos.

El país de afiliación sirve como barrera operacional pedida por el proyecto. [NO VERIFICADO] No se ha acreditado que sea el único factor que determina las leyes aplicables a una persona o tratamiento. Revisar también establecimiento, residencia, destinatarios y proveedores antes de aprobar.

## Unión Europea: marco común verificado

- [VERIFICADO: https://www.cnil.fr/fr/les-bases-legales/interet-legitime] El interés legítimo exige interés identificable, necesidad y ponderación de derechos. [NO VERIFICADO] Que el perfilado público y la puntuación concreta de KOL Radar superen esa ponderación; requiere evaluación documentada antes de activarse.
- [VERIFICADO: https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre3] RGPD arts.12, 14, 18 y 21: información al obtener datos indirectamente, como máximo un mes y antes de la primera comunicación o divulgación cuando corresponda; oposición al interés legítimo y al perfilado asociado; respuesta sin dilación y máximo un mes, prorrogable en condiciones legales; limitación mientras se verifica una oposición. La oposición a marketing directo impide continuar ese uso.
- [VERIFICADO: https://www.cnil.fr/sites/cnil/files/atoms/files/wp260_enpdf_transparency.pdf] La excepción por esfuerzo desproporcionado del art.14.5.b requiere evaluación de impacto frente al esfuerzo y salvaguardas, incluido aviso público. [NO VERIFICADO] Que corresponda a KOL Radar; ni fuente pública ni volumen bastan por sí solos.
- [VERIFICADO: https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre4] Art.27: representante para responsables extracomunitarios comprendidos en art.3.2, con excepciones limitadas; art.30: registro de actividades. [NO VERIFICADO] Aplicabilidad concreta, DPO y evaluación de impacto para esta operación.
- [VERIFICADO: https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre5] Transferencias sujetas al capítulo V: adecuación, garantías o excepciones correspondientes. [NO VERIFICADO] Mecanismo válido para el flujo real de KOL Radar, Chile, GitHub y el servicio de solicitudes.

Propuesta común: `allowed_with_conditions`, certeza `media`, `plazo_respuesta_dias: 28` como objetivo operacional conservador, **no como plazo legal de 28 días**. Plazo legal: un mes calendario; bloqueo interno inmediato al verificarse una solicitud. Las condiciones incluyen evaluación de interés legítimo, aviso indirecto efectivo o excepción fundada, revisión de perfilado, representante cuando corresponda, transferencias documentadas y revisión nacional.

Cada fila hereda todas las fuentes y condiciones del marco común anterior. [NO VERIFICADO] No se revisaron leyes nacionales complementarias ni requisitos sectoriales de cada Estado; una aprobación debe resolver esa brecha individualmente.

| ISO2 | País | Propuesta | Certeza | Revisión nacional |
|---|---|---|---|---|
| AT | Austria | allowed_with_conditions | media | [NO VERIFICADO] |
| BE | Bélgica | allowed_with_conditions | media | [NO VERIFICADO] |
| BG | Bulgaria | allowed_with_conditions | media | [NO VERIFICADO] |
| HR | Croacia | allowed_with_conditions | media | [NO VERIFICADO] |
| CY | Chipre | allowed_with_conditions | media | [NO VERIFICADO] |
| CZ | Chequia | allowed_with_conditions | media | [NO VERIFICADO] |
| DK | Dinamarca | allowed_with_conditions | media | [NO VERIFICADO] |
| EE | Estonia | allowed_with_conditions | media | [NO VERIFICADO] |
| FI | Finlandia | allowed_with_conditions | media | [NO VERIFICADO] |
| FR | Francia | allowed_with_conditions | media | [NO VERIFICADO] normativa nacional complementaria |
| DE | Alemania | allowed_with_conditions | media | [NO VERIFICADO] |
| GR | Grecia | allowed_with_conditions | media | [NO VERIFICADO] |
| HU | Hungría | allowed_with_conditions | media | [NO VERIFICADO] |
| IE | Irlanda | allowed_with_conditions | media | [NO VERIFICADO] |
| IT | Italia | allowed_with_conditions | media | [NO VERIFICADO] |
| LV | Letonia | allowed_with_conditions | media | [NO VERIFICADO] |
| LT | Lituania | allowed_with_conditions | media | [NO VERIFICADO] |
| LU | Luxemburgo | allowed_with_conditions | media | [NO VERIFICADO] |
| MT | Malta | allowed_with_conditions | media | [NO VERIFICADO] |
| NL | Países Bajos | allowed_with_conditions | media | [NO VERIFICADO] |
| PL | Polonia | allowed_with_conditions | media | [NO VERIFICADO] |
| PT | Portugal | allowed_with_conditions | media | [NO VERIFICADO] |
| RO | Rumania | allowed_with_conditions | media | [NO VERIFICADO] |
| SK | Eslovaquia | allowed_with_conditions | media | [NO VERIFICADO] |
| SI | Eslovenia | allowed_with_conditions | media | [NO VERIFICADO] |
| ES | España | allowed_with_conditions | media | [NO VERIFICADO] |
| SE | Suecia | allowed_with_conditions | media | [NO VERIFICADO] |

## Reino Unido — GB

Propuesta `allowed_with_conditions`, certeza media, plazo operacional 28 días; bloqueo interno inmediato verificado.

- [VERIFICADO: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/legitimate-interests/] La ICO mantiene guía de interés legítimo, actualizada el 23-03-2026 por Data (Use and Access) Act; usa examen de finalidad, necesidad y balance. [NO VERIFICADO] Resultado favorable para KOL Radar.
- [VERIFICADO: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/right-to-be-informed/] Fuentes públicas también requieren aviso; máximo un mes y antes de divulgación cuando corresponda. Excepción por esfuerzo desproporcionado requiere justificarla; la ICO indica DPIA cuando se invoca imposibilidad/esfuerzo desproporcionado. La guía está bajo revisión por la reforma.
- [VERIFICADO: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/right-to-object/] Oposición: un mes calendario, sin dilación indebida; marketing directo: cese absoluto; otros casos pueden requerir motivos imperiosos. ICO sugiere 28 días como periodo fijo operacional.
- [NO VERIFICADO] Representante británico, tasa/registro ICO, transferencias y todas las disposiciones vigentes tras reforma para el responsable específico. Condición de activación: resolverlos con revisión jurídica local y documentar base, transparencia y flujo internacional.

## Suiza — CH

Propuesta `blocked`, certeza baja sobre habilitación del producto, plazo legal `null`.

- [VERIFICADO: https://www.edoeb.admin.ch/en/representatives-in-accordance-with-article-14-fadp] La LPD/FADP art.14 exige representante si concurren oferta/monitoreo en Suiza, escala, regularidad y alto riesgo. [NO VERIFICADO] Que este proyecto reúna todas las condiciones.
- [VERIFICADO: https://www.edoeb.admin.ch/en/cross-border-transfer-of-personal-data] Arts.16–17: adecuación, garantías o excepción para transferir; art.19: informar sobre divulgación exterior. [NO VERIFICADO] Salvaguarda concreta para GitHub/Chile.
- [VERIFICADO: https://www.edoeb.admin.ch/en/duty-to-provide-information] La autoridad dispone orientación sobre deber de información. [NO VERIFICADO] Base suficiente para perfilado público, excepción indirecta aplicable, plazos de derechos y registro para KOL Radar. Bloqueado pese a más de dos fuentes: faltan extremos esenciales.

## Turquía — TR

Propuesta `allowed_with_conditions`, certeza media, respuesta 30 días; bloqueo inmediato como política del producto.

- [VERIFICADO: https://www.kvkk.gov.tr/Icerik/6649/Personal-Data-Protection-Law] Ley 6698 art.5 contempla datos publicados por el propio titular e interés legítimo sujeto a derechos; art.10 información; art.11 derechos incluida oposición a consecuencias adversas del análisis exclusivamente automatizado; art.13 respuesta máximo 30 días; art.9 modificado en 2024 establece mecanismos de transferencia exterior. [NO VERIFICADO] Que una fuente bibliográfica permita publicar y puntuar a su autor, que aplique una exención de información o que el flujo internacional esté cubierto.
- [VERIFICADO: https://www.kvkk.gov.tr/Icerik/6650/VERBIS] Registro previo de responsables como regla del art.16. [NO VERIFICADO] Exención y representante específicos de este operador. No usar como actual una guía de transferencias anterior a la reforma de 2024.
- Condiciones: abogado local valida interés legítimo, deber de información, VERBIS/representación y mecanismo internacional antes de aprobación.

## Australia — AU

Propuesta `allowed_with_conditions`, certeza media, plazo legal `null`; no inventar plazo uniforme de oposición. Bloqueo inmediato como política interna.

- [VERIFICADO: https://www.oaic.gov.au/privacy/australian-privacy-principles/australian-privacy-principles-guidelines/chapter-3-app-3-collection-of-solicited-personal-information] APP3 exige necesidad razonable, proporcionalidad y medios lícitos y justos; recoger de terceros exige excepción a obtención directa. La publicación en Internet no autoriza reutilización irrestricta; generar inferencias constituye recolección. [NO VERIFICADO] Que perfilado y puntuación satisfagan estas condiciones.
- [VERIFICADO: https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/more-guidance/guide-to-data-analytics-and-the-australian-privacy-principles] APP5 información, APP7 opt-out para marketing directo y APP8 obligaciones de divulgación internacional. Receptores internacionales pueden generar responsabilidad para el remitente.
- [NO VERIFICADO] Alcance territorial y material de Privacy Act sobre este operador, representante/registro, plazo concreto de cada derecho y excepción al aviso indirecto. Condiciones: resolver cada punto, evaluar tratamiento justo y aviso antes de activar.

## Jurisdicciones bloqueadas por investigación insuficiente

Para cada país de esta sección: `estado_propuesto: blocked`, `estado_aprobado: null`, `certeza: baja`, `plazo_respuesta_dias: null`. El bloqueo preventivo interno es inmediato; no se atribuye a una ley. [NO VERIFICADO] Base que habilite el perfilado público de KOL Radar, deber/excepción de aviso indirecto, derecho general de oposición y plazo, representante/registro aplicable, mecanismo internacional y aplicación territorial. Se requiere investigación adicional y abogado local antes de activar. Las afirmaciones concretas que sí se pudieron verificar se indican debajo.

### Israel — IL

[NO VERIFICADO] El intento de abrir https://www.gov.il/he/pages/tikun13_qa?chapterIndex=6 falló. No se verificaron dos fuentes primarias legibles. No incorporar esa URL como fuente legal verificada.

### Arabia Saudita — SA

[NO VERIFICADO] Estos documentos de SDAIA devolvieron «Request Rejected»: https://sdaia.gov.sa/en/SDAIA/about/Documents/Personal%20Data%20English%20V2-23April2023-%20Reviewed-.pdf y https://sdaia.gov.sa/en/Research/Documents/ExecutiveRegulations.pdf. Los fragmentos del buscador no sustituyen abrir y revisar el texto. Cero documentos legibles verificados en esta revisión.

### Emiratos Árabes Unidos — AE

[NO VERIFICADO] Falló la apertura de https://u.ae/en/about-the-uae/digital-uae/data/data-protection-laws. No se verificaron dos fuentes ni la distinción de regímenes territoriales. Cero documentos legibles verificados.

### Sudáfrica — ZA

- [VERIFICADO: https://inforegulator.org.za/acts/] La autoridad lista POPIA y normas relacionadas. Esto no verifica por sí mismo toda disposición material.
- [VERIFICADO: https://inforegulator.org.za/popia/] La autoridad indica registro de Information Officers conforme a sección 55 y trámites de corrección/supresión y otras solicitudes.
- [NO VERIFICADO] Base, excepción de aviso y transferencia aplicables al producto y plazos. Se mantiene blocked aunque se abrieron dos páginas: no se completó revisión del texto legal.

### Egipto — EG

[NO VERIFICADO] https://www.pdpc.gov.eg/ redirigió a https://portal.pdpc.gov.eg/ sin texto legible. No se verificaron dos fuentes primarias. No atribuir plazos, licencias o reformas recientes basándose solo en resultados del buscador.

### India — IN

- [VERIFICADO: https://www.meity.gov.in/static/uploads/2024/02/Digital-Personal-Data-Protection-Act-2023-1.pdf] Se abrió el texto de DPDP Act 2023. Sección 3 delimita alcance territorial y extraterritorial y excluye ciertos datos hechos públicos por su titular o por obligación legal; no equivale a toda información accesible en Internet.
- [NO VERIFICADO] La página de reglas 2025 https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa?pageTitle=Digital-Personal-Data-Protection-Rules-2025 abrió sin texto. Vigencia escalonada y reglamentación no verificadas. Solo un documento sustantivo verificado; blocked.

### China — CN

[NO VERIFICADO] Fallaron aperturas de https://en.npc.gov.cn.cdurl.cn/2021-12/29/c_694559_2.htm y https://en.npc.gov.cn/2021-12/29/c_694559.htm. No se verificaron dos fuentes primarias. No convertir el fragmento de buscador sobre art.27 PIPL en permiso para publicar.

### Japón — JP

- [VERIFICADO: https://www.ppc.go.jp/en/legal/] La PPC publica índice legal APPI y advierte que solo el texto japonés tiene efecto legal; el índice remite a consolidación de abril de 2023.
- [VERIFICADO: https://www.ppc.go.jp/files/pdf/APPI_english.pdf] Se abrió traducción tentativa fechada junio de 2020. **No acredita legislación vigente en 2026.**
- [NO VERIFICADO] Revisión actual de cesión pública a terceros, eventual mecanismo de opt-out/notificación a PPC y transferencias. Blocked aunque hay dos documentos: antigüedad e insuficiencia material.

### Corea del Sur — KR

- [VERIFICADO: https://pipc.go.kr/eng/user/lgp/law/lawsRegulations.do] PIPC publica índice de PIPA y decreto con fecha de vigencia 15-09-2023.
- [VERIFICADO: https://www.law.go.kr/LSW/lsInfoP.do?chrClsCd=010202&lsiSeq=248613&urlMode=engLsInfoR&viewCls=engLsInfoR] Se abrió una página histórica identificada como PIPA 2023; el contenido legal completo no quedó accesible en la lectura realizada.
- [NO VERIFICADO] Versión vigente, base y todos los requisitos del tratamiento propuesto. El segundo enlace no se cuenta como segunda fuente sustantiva suficiente.

### Singapur — SG

- [VERIFICADO: https://www.pdpc.gov.sg/-/media/Files/PDPC/PDF-Files/EU-GDPR/Broad-Comparison-of-the-PDPAs-Consent-Exceptions-with-EU-GDPRs-Legal-Bases-for-Processing-Personal-Data-1-Apr-2021.pdf?la=en] Comparación oficial describe excepciones por datos públicamente disponibles e intereses legítimos que superan efectos adversos; no prueba que correspondan al producto.
- [NO VERIFICADO] SSO y páginas HTML de PDPC fallaron o mostraron captcha. Solo un documento legible; no se verificó ley consolidada, aviso, derechos, DPO ni transferencias. Blocked.

### Rusia — RU

- [VERIFICADO: https://mintrud.gov.ru/docs/laws/130] Portal oficial publica Ley federal 152-FZ sobre datos personales.
- [NO VERIFICADO] Vigencia de cada reforma, tratamiento de datos permitidos para divulgación, localización, notificaciones, transferencias, plazos y habilitación de KOL Radar. Solo una fuente; blocked.

## Indicaciones al integrador

1. No contar URLs fallidas como `fuentes_legales`; dejarlas en esta bitácora de brechas.
2. No convertir `null` en 30 días. Los países bloqueados no necesitan un plazo legal inventado. Si el procesador exige un entero, usar SLA interno separado, claramente rotulado, sin rebautizarlo plazo legal.
3. `plazo_bloqueo: "inmediato"` puede ser compromiso operacional para todas las solicitudes verificadas; no presentarlo como mandato uniforme de leyes distintas.
4. El mínimo de dos fuentes es necesario, no suficiente. Suiza, Sudáfrica y Japón siguen bloqueados por brechas sustantivas.
5. Cada fila UE hereda referencias comunes, pero debe conservar la condición de revisión nacional pendiente. Ninguna fuente aquí da una autorización particular a KOL Radar.
