"""Casos de prueba compartidos por los tests y por evalua.py."""

# Consultas con sinónimos o paráfrasis: ninguna palabra de la consulta está en las notas buscadas.
SINONIMOS = [
    ("respaldar ficheros para no perderlos",
     {"Copias de seguridad con Restic", "Backups con Restic", "Regla 3-2-1 de copias"}),
    ("aprovechar restos de comida para abonar",
     {"Compostaje doméstico", "Hacer compost en casa"}),
    ("método para concentrarme sin distraerme",
     {"Técnica Pomodoro", "Trabajar en bloques de 25 minutos"}),
    ("poner por escrito lo dicho en una entrevista grabada",
     {"Transcribir audio con Whisper"}),
    ("tengo insomnio y no descanso por las noches",
     {"Higiene del sueño"}),
    ("cuadrar las cuentas de casa",
     {"Presupuesto mensual", "Hoja de cálculo de gastos", "2026-10-28 Revisión de gastos"}),
    ("guardar alimentos mucho tiempo sin que se estropeen",
     {"Fermentar verduras"}),
]

# Textos de notas nuevas y qué notas existentes deberían saltar como posible duplicado.
DUPLICADOS = [
    ("Backups cifrados con Restic: instantáneas incrementales y deduplicación de bloques.",
     {"Copias de seguridad con Restic", "Backups con Restic"}),
    ("Compost en casa: capas verdes de peladuras y posos de café, capas marrones de cartón y hojas secas, "
     "voltear cada semana y mantener húmedo.",
     {"Compostaje doméstico", "Hacer compost en casa"}),
]
# Paráfrasis sin apenas palabras en común: solo el buscador por significado debería verlas.
DUPLICADOS_PARAFRASIS = [
    ("Estudiar con un cronómetro: veinticinco minutos de esfuerzo concentrado y cinco de reposo, "
     "y cada cuatro rondas una pausa mayor.",
     {"Técnica Pomodoro", "Trabajar en bloques de 25 minutos"}),
]
NO_DUPLICADOS = [
    "Receta de gazpacho andaluz con tomate, pepino, pimiento y aceite de oliva.",
    "Configurar el router wifi de casa con una contraseña nueva.",
    "Resumen de la reunión de la comunidad de vecinos sobre el ascensor.",
]
