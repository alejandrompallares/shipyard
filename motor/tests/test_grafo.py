from motor_notas.indice import Indice


def test_enlaces_backlinks_y_dos_saltos(boveda, ruta_indice):
    r = Indice(boveda, ruta_indice).relacionadas("Huerto en el balcón")
    assert set(r["enlaza_a"]) == {"Jardinería en macetas", "Riego por goteo", "Rotación de cultivos",
                                  "Compostaje doméstico", "2026-09-12 Plan del huerto"}
    assert set(r["enlazada_desde"]) == {"Jardinería en macetas", "Compostaje doméstico",
                                        "2026-09-12 Plan del huerto", "Mapa general"}
    dos = {d["titulo"]: d["via"] for d in r["a_dos_saltos"]}
    assert dos["Web de recetas familiares"] == ["Mapa general"]
    assert "Huerto en el balcón" not in dos
    assert not set(dos) & set(r["enlaza_a"])  # lo directo no se repite
    assert r["enlaces_rotos"] == []


def test_resuelve_sin_acentos_ni_mayusculas(boveda, ruta_indice):
    r = Indice(boveda, ruta_indice).relacionadas("[[huerto en el BALCON]]")
    assert r["nota"] == "Huerto en el balcón"


def test_enlaces_rotos(boveda, ruta_indice):
    (boveda / "00 Inbox" / "Suelta.md").write_text("Ver [[No existe]] y [[Syncthing]].\n", encoding="utf-8")
    r = Indice(boveda, ruta_indice).relacionadas("Suelta")
    assert r["enlaces_rotos"] == ["No existe"]
    assert r["enlaza_a"] == ["Syncthing"]


def test_nota_inexistente(boveda, ruta_indice):
    assert "error" in Indice(boveda, ruta_indice).relacionadas("Nada de nada")
