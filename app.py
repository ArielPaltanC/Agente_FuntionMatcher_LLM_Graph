# =========================================
# IMPORTS
# =========================================
from typing import TypedDict, List
from collections import Counter
import re, json

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from neo4j import GraphDatabase
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "password")
driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

from langgraph.graph import StateGraph, END
from openai import OpenAI
import os
os.environ["OPENAI_API_KEY"] = "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"

# =========================================
# OPENAI CLIENT
# =========================================
client = OpenAI()

LOGS = []

def log(msg):
    LOGS.append(msg)


# =========================================
# EMBEDDINGS (COSENO)
# =========================================
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    encode_kwargs={"normalize_embeddings": True}
)

# =========================================
# TOOLS DEFINICIÓN (10 FUNCIONES)
# =========================================
TOOLS = [

{
"name": "buscar_producto",
"description": "Permite consultar y mostrar productos del catálogo según lo que el cliente desea comprar o explorar.",
"examples": [
"quiero ver productos","mostrar catálogo","qué venden",
"recomiéndame ropa","ver opciones", "tiene camisas",
"necesito una camisa","buscar prendas"
]
},

{
"name": "consultar_stock",
"description": "Verifica la disponibilidad o existencias de un producto antes de la compra.",
"examples": [
"tienen disponible","hay stock","queda inventario",
"tienen talla M","hay existencias","disponible ahora",
"queda en bodega","todavía hay unidades","tienen esta camisa en talla M"
]
},

{
"name": "estado_pedido",
"description": "Consulta el estado actual de un pedido o envío realizado.",
"examples": [
"dónde está mi pedido","rastrear envío","seguimiento de compra",
"estado de orden","mi paquete","tracking pedido",
"ya enviaron","ver envío"
]
},

{
"name": "cancelar_pedido",
"description": "Cancela o anula un pedido existente antes de su entrega.",
"examples": [
"cancelar pedido","anular compra","no quiero la orden",
"cancelar envío","detener pedido","quiero cancelar","eliminar orden"
]
},

{
"name": "devoluciones",
"description": "Gestiona devoluciones, reembolsos o retornos de productos comprados.",
"examples": [
"quiero devolver","hacer devolución","reembolso",
"producto defectuoso","retornar compra",
"devolver artículo","quiero mi dinero"
]
},

{
"name": "metodos_pago",
"description": "Informa los medios y formas de pago disponibles.",
"examples": [
"formas de pago","cómo puedo pagar","aceptan tarjeta",
"pago con transferencia","medios de pago",
"tarjeta o efectivo","pago en cuotas"
]
},

{
"name": "horarios_atencion",
"description": "Proporciona los horarios de atención de la tienda o soporte.",
"examples": [
"horarios de atención","a qué hora abren","cierran hoy",
"horario tienda","horario soporte",
"cuándo atienden","horas de servicio"
]
},

{
"name": "direccion_tienda",
"description": "Entrega la ubicación o dirección física de la tienda.",
"examples": [
"dónde están ubicados","dirección tienda","ubicación local",
"cómo llegar","mapa tienda","dónde queda","ubicación física"
]
},

{
"name": "contactar_soporte",
"description": "Escala la conversación a soporte humano.",
"examples": [
"hablar con soporte","necesito ayuda humana",
"agente humano","atención al cliente",
"soporte técnico","contactar asesor","hablar con operador"
]
},

{
"name": "recomendaciones",
"description": "Genera recomendaciones de productos.",
"examples": [
"qué me recomiendas","sugerencias","productos recomendados",
"lo más vendido","tendencias","mejor opción","qué elegir"
]
},

{
"name": "crear_pedido",
"description": "Crea una orden de compra cuando el cliente confirma que desea adquirir productos con cantidad definida.",
"examples": [
"quiero comprar 3 camisas",
"quiero comprar esto",
"quiero llevar estas camisas",
"deseo comprar", "llevar",
"hazme el pedido",
"crear orden de compra",
"comprar ahora",
"confirmar compra"
]
}

]

# =========================================
# DOCUMENTOS + FAISS
# =========================================
docs = []
for tool in TOOLS:
    for ex in tool["examples"]:
        docs.append(
            Document(
                page_content=ex,
                metadata={
                    "name": tool["name"],
                    "description": tool["description"]
                }
            )
        )

vector_store = FAISS.from_documents(
    docs,
    embeddings,
    distance_strategy="MAX_INNER_PRODUCT"
)
#####################################################################
def es_consulta_tienda(query: str) -> bool:
    prompt = f"""
Responde SOLO con una palabra: SI o NO.

La siguiente consulta está relacionada con una tienda de ropa
(productos, compras, pedidos, pagos, horarios, ubicación o soporte)?

Consulta:
"{query}"
"""

    r = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    respuesta = r.output_text.strip().upper()
    return respuesta.startswith("SI")

# =========================================
# ROUTER → TOP 3 (DEDUPLICADO)
# =========================================
def seleccionar_top_k(query, k=3):
    results = vector_store.similarity_search_with_score(query, k=10)

    mejores = {}
    for doc, score in results:
        name = doc.metadata["name"]
        desc = doc.metadata["description"]
        if name not in mejores or score > mejores[name]["score"]:
            mejores[name] = {
                "name": name,
                "description": desc,
                "score": score
            }

    ordenadas = sorted(mejores.values(), key=lambda x: x["score"], reverse=True)
    return ordenadas[:k]

# =========================================
# UTILIDADES
# =========================================
def detectar_cantidad(texto):
    m = re.search(r"\b(\d+)\b", texto)
    return int(m.group(1)) if m else None

def es_exploracion(texto):
    return any(v in texto.lower() for v in ["buscar", "ver", "mostrar"])

def es_saludo(texto):
    return texto.lower().strip() in [
        "hola", "buenos dias", "buenas tardes", "buenas noches", "hey"
    ]

# =========================================
# GPT: RESPUESTA NATURAL
# =========================================
def responder_cordial(texto):
    prompt = f"""
Eres un asistente de una tienda de ropa.
Responde de forma cordial y profesional.
Si no es una consulta directa de compra, redirige amablemente.

Mensaje:
"{texto}"
"""
    r = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return r.output_text

# =========================================
# GRAFO DE FUNCIONES 
# =========================================
def obtener_plan_desde_neo4j(funcion):
    query = """
    MATCH (f:Function {name: $funcion})-[r:NEXT]->(p:Function)
    RETURN p.name AS paso, r.step AS step
    ORDER BY step ASC
    """

    with driver.session() as session:
        result = session.run(query, funcion=funcion)
        pasos = [r["paso"] for r in result]

    return pasos


# =========================================
# BACKEND (SOLO PRINTS)
# =========================================
INTERNAL_FUNCTIONS = {
    "obtener_info_cliente": lambda: log("El pedido llegará en aproxmiadamente 2 dias"),
    "generar_recomendacion": lambda: log("Uno de nuestros empleados lo ayudará a decidir según sus gustos"),
    "info_devoluciones": lambda: (log("Para realizar una devolución debe realizarce hasta 2 dias después de la entrega del pedido"),log("Se ha realizado el reembolso")),
    "obtener_info_producto": lambda: log("obteniendo información del producto"),
    "consultar_stock_backend": lambda: log(" consultando stock"),
    "ver_horarios": lambda: log("Estamos abiertos todos los dias, desde las 9-am hasta las 8-pm"),
    "ver_direccion": lambda: log("Estamos ubicados entre la calle Gran Colombia y Presidente Borrero"),
    "ayuda": lambda: (log("Contactando con el personal de soporte"),log("Un empleado se contactara con usted en 1 minuto")),
    "ver_metodos_pago": lambda: (log("consultando metodos de pago"),log("disponesmo pagos en efectivo y con tarjeta de credito/debito")),
    "crear_pedido_backend": lambda: (
        log("🛒 creando pedido"),
        log("✅ pedido creado")
    ),
    "cancelar_pedido_backend": lambda: (
        log("❌ cancelando pedido"),
        log("✅ pedido cancelado")
    )
}

# =========================================
# LANGGRAPH STATE
# =========================================
class AgentState(TypedDict):
    query: str
    funcion: str
    plan: List[str]
    resultado: str

# =========================================
# LANGGRAPH NODES
# =========================================
def node_planificador(state: AgentState) -> AgentState:
    log("🧭 Explorando grafo en Neo4j...")

    plan = obtener_plan_desde_neo4j(state["funcion"])

    log("📋 Plan generado:")
    for i, p in enumerate(plan, 1):
        log(f"{i}. {p}()")

    state["plan"] = plan
    return state


def node_ejecutor(state: AgentState) -> AgentState:
    log("\n⚙️ Ejecutando plan paso a paso...\n")
    for paso in state["plan"]:
        log(f"➡️ Ejecutando {paso}()")
        INTERNAL_FUNCTIONS[paso]()
    state["resultado"] = f"Proceso {state['funcion']} ejecutado correctamente"
    return state

def node_respuesta(state: AgentState) -> AgentState:
    respuesta = responder_cordial(state["resultado"])
    log(f"🤖 {respuesta}")
    return state


# =========================================
# CONSTRUIR LANGGRAPH
# =========================================
graph = StateGraph(AgentState)

graph.add_node("planificador", node_planificador)
graph.add_node("ejecutor", node_ejecutor)
graph.add_node("respuesta", node_respuesta)

graph.set_entry_point("planificador")
graph.add_edge("planificador", "ejecutor")
graph.add_edge("ejecutor", "respuesta")
graph.add_edge("respuesta", END)

agent_graph = graph.compile()

def ejecutar_agente(query):
    global LOGS
    LOGS = []

    # 0️⃣ FILTRO DE DOMINIO (LLM)
    if not es_consulta_tienda(query):
        respuesta = responder_cordial(
            "Puedo ayudarte con productos, pedidos y servicios de nuestra tienda de ropa."
        )
        log(respuesta)

        return {
            "top3": [],
            "funcion": "fuera_de_dominio",
            "logs": LOGS
        }

    # 1️⃣ Saludo
    if es_saludo(query):
        log(responder_cordial(query))
        return {
            "top3": [],
            "funcion": "saludo",
            "logs": LOGS
        }

    # 2️⃣ Router semántico (solo si es tienda)
    top3 = seleccionar_top_k(query)

    seleccion = top3[0]
    funcion = seleccion["name"]

    cantidad = detectar_cantidad(query)
    exploracion = es_exploracion(query)

    state = {
        "query": query,
        "funcion": funcion,
        "plan": [],
        "resultado": ""
    }

    agent_graph.invoke(state)

    return {
        "top3": top3,
        "funcion": funcion,
        "logs": LOGS
    }



