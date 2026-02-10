# Agente con Function Matcher, Exploración, Planes y Ejecución de Tareas mediante gestión de Grafos y Estados. 

Este proyecto simula un agente de Inteligencia Artificial para una tienda de ropa, capaz de interpretar consultas en lenguaje natural, decidir la acción correcta, planificar un flujo de ejecución mediante un grafo y ejecutar dicho plan paso a paso.

El sistema combina **embeddings semánticos**, **razonamiento simbólico**, **planificación basada en grafos** y **ejecución controlada**.

---

## Tecnologías Utilizadas

- **Python 3**
- **LangChain** (embeddings y vector store)
- **FAISS** (búsqueda semántica)
- **LangGraph** (planner y ejecución de flujo)
- **Neo4j** (grafo de planificación persistente)
- **OpenAI GPT-4.1 Mini** (LLM)
- **Streamlit** (frontend)
- **Docker** (Neo4j)

---

## Arquitectura General

1. El usuario ingresa una consulta.
2. La consulta es evaluada semánticamente mediante embeddings.
3. Se seleccionan las 3 funciones más probables (Top-K).
4. Se aplica una regla de negocio para validar la acción.
5. La función final se envía al planner.
6. El planner consulta Neo4j para generar el plan.
7. El plan se ejecuta paso a paso.
8. El agente genera una respuesta al usuario.

---

## Funciones Soportadas (Planner)

El sistema reconoce y planifica las siguientes funciones:

- buscar_producto  
- consultar_stock  
- crear_pedido  
- estado_pedido  
- cancelar_pedido  
- devoluciones  
- metodos_pago  
- recomendaciones  
- horarios_atencion  
- direccion_tienda  
- contactar_soporte  

Cada función tiene un **plan distinto** definido en el grafo de Neo4j.

---

## Grafo de Planificación (Neo4j)

El flujo de ejecución está modelado como un grafo dirigido, donde:

- Cada nodo representa una función del sistema.
- Cada relación `NEXT` indica el siguiente paso del plan.
- Las relaciones contienen un atributo `step` que define el orden de ejecución.

### Ejemplo de Plan (`crear_pedido`)

1. obtener_info_producto  
2. consultar_stock_backend  
3. ver_metodos_pago  
4. crear_pedido_backend  

---

## Visualización del Grafo

A continuación se muestra el grafo de planificación cargado en Neo4j:

<img width="1082" height="1274" alt="Image" src="https://github.com/user-attachments/assets/b336dbd8-fa27-407e-a2e7-c0b01b8597d8" />

---
## Conclusiones

Este proyecto permitió desarrollar un agente inteligente híbrido que integra procesamiento de lenguaje natural, razonamiento simbólico y planificación basada en grafos para atender consultas de una tienda de ropa de forma estructurada y confiable.

El uso de embeddings semánticos permitió identificar la intención del usuario de manera flexible, mientras que las reglas de negocio aseguraron decisiones correctas, evitando acciones incorrectas como la creación de pedidos sin información suficiente. La incorporación de Neo4j permitió modelar y persistir los flujos de ejecución mediante grafos, facilitando la planificación ordenada y la escalabilidad del sistema.

Finalmente, LangGraph permitió ejecutar los planes de forma controlada y paso a paso, demostrando cómo un agente de IA puede razonar, planificar y actuar de manera transparente, cumpliendo con los objetivos académicos propuestos.

---

## Autores
 - Ariel Paltán. arielpaltan203@hotmail.com
 - Diego Bravo. brzoale2510@gmail.com 

## Instalación y Ejecución

### Requisitos

- Python 3.10+
- Docker Desktop
- Conexión a internet (OpenAI API)

---

### Instalar dependencias

```bash
python -m pip install -r requirements.txt
