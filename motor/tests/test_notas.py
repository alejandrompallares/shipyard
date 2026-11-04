from motor_notas.notas import parsear, validar_titulo


def test_campos_al_principio_y_enlaces():
    n = parsear("tipo:: herramienta\nestado:: activo\n\nTexto con [[Otra nota]], [[Alias|visible]] y "
                "[[Carpeta/Tercera#sección]].\nno-es-campo:: aquí ya no", "X", "20 Intereses/X.md")
    assert n.campos == {"tipo": "herramienta", "estado": "activo"}
    assert n.enlaces == ["Otra nota", "Alias", "Tercera"]
    assert n.carpeta == "20 Intereses"
    assert "no-es-campo:: aquí ya no" in n.cuerpo


def test_reglas_de_titulo():
    assert validar_titulo("Copias de seguridad con Restic") is None
    assert validar_titulo("2026-10-02 Diseño de la web") is None
    for malo in ["Restic (copias)", "Restic, copias", "Nota: algo", "a/b", "", "   "]:
        assert validar_titulo(malo), malo
