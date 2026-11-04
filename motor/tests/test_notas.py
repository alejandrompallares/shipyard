from motor_notas.notas import parsear, validar_titulo


def test_campos_al_principio_y_enlaces():
    n = parsear("tipo:: herramienta\nestado:: activo\n\nTexto con [[Otra nota]], [[Alias|visible]] y "
                "[[Carpeta/Tercera#sección]].\nno-es-campo:: aquí ya no", "X", "20 Intereses/X.md")
    assert n.campos == {"tipo": "herramienta", "estado": "activo"}
    assert n.enlaces == ["Otra nota", "Alias", "Tercera"]
    assert n.carpeta == "20 Intereses"
    assert "no-es-campo:: aquí ya no" in n.cuerpo


def test_bloque_yaml_de_jylos():
    texto = ("---\nid: 20 Intereses/X.md\ntitle: X\ndeleted: false\ntags:\n - ia-local\n - modelos\n---\n\n"
             "tipo:: herramienta\nsirve-para:: probar [[Otra]]\n\nTexto de la nota.\n")
    n = parsear(texto, "X", "20 Intereses/X.md")
    assert n.campos == {"tipo": "herramienta", "sirve-para": "probar [[Otra]]", "etiquetas": "ia-local modelos"}
    assert n.cuerpo == "Texto de la nota."
    assert n.enlaces == ["Otra"]
    assert "deleted" not in n.texto_busqueda()


def test_bloque_yaml_sin_etiquetas():
    n = parsear("---\ntitle: X\n---\ntipo:: idea\n\nHola", "X", "X.md")
    assert n.campos == {"tipo": "idea"}
    assert n.cuerpo == "Hola"


def test_linea_horizontal_no_es_yaml():
    texto = "---\nTexto entre líneas.\n---\nMás texto."
    n = parsear(texto, "X", "X.md")
    assert n.campos == {}
    assert n.cuerpo == texto


def test_reglas_de_titulo():
    assert validar_titulo("Copias de seguridad con Restic") is None
    assert validar_titulo("2026-10-02 Diseño de la web") is None
    for malo in ["Restic (copias)", "Restic, copias", "Nota: algo", "a/b", "", "   "]:
        assert validar_titulo(malo), malo
