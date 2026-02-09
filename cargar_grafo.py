from neo4j import GraphDatabase

# ===============================
# CONEXIÓN A NEO4J
# ===============================
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

# ===============================
# TU GRAFO DE FUNCIONES
# ===============================
FUNCTION_GRAPH = {
    "buscar_producto": ["obtener_info_producto"],
    "consultar_stock": ["obtener_info_producto", "consultar_stock_backend"],
    "crear_pedido": [
        "obtener_info_producto",
        "consultar_stock_backend",
        "ver_metodos_pago",
        "crear_pedido_backend"
    ],
    "estado_pedido": [
        "obtener_info_producto",
        "consultar_stock_backend",
        "ver_metodos_pago",
        "crear_pedido_backend",
        "obtener_info_cliente"
    ],
    "cancelar_pedido": [
        "obtener_info_producto",
        "consultar_stock_backend",
        "ver_metodos_pago",
        "crear_pedido_backend",
        "cancelar_pedido_backend"
    ],
    "devoluciones": [
        "obtener_info_producto",
        "consultar_stock_backend",
        "ver_metodos_pago",
        "crear_pedido_backend",
        "info_devoluciones"
    ],
    "metodos_pago": [
        "obtener_info_producto",
        "consultar_stock_backend",
        "ver_metodos_pago"
    ],
    "recomendaciones": ["ayuda", "generar_recomendacion"],
    "horarios_atencion": ["ver_horarios"],
    "direccion_tienda": ["ver_direccion"],
    "contactar_soporte": ["ayuda"]
}

# ===============================
# CREAR GRAFO
# ===============================
def crear_grafo():
    with driver.session() as session:
        # 1️⃣ LIMPIAR GRAFO (solo para setup)
        session.run("MATCH (n) DETACH DELETE n")

        # 2️⃣ CREAR NODOS Y RELACIONES
        for origen, destinos in FUNCTION_GRAPH.items():
            session.run(
                "MERGE (:Function {name: $name})",
                name=origen
            )

            for idx, destino in enumerate(destinos, start=1):
                session.run(
                    """
                    MERGE (a:Function {name: $origen})
                    MERGE (b:Function {name: $destino})
                    MERGE (a)-[r:NEXT {step: $step}]->(b)
                    """,
                    origen=origen,
                    destino=destino,
                    step=idx
                )

    print("✅ Grafo de funciones creado en Neo4j")

# ===============================
# EJECUTAR
# ===============================
crear_grafo()
driver.close()
