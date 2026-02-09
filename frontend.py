import streamlit as st
from app import ejecutar_agente

st.set_page_config(
    page_title="Agente de Tienda IA",
    page_icon="🧠",
    layout="centered"
)

st.title("Tienda de Ropa")

query = st.text_input("✍️ Escribe tu consulta:")

if st.button("Ejecutar agente"):
    if query.strip() == "":
        st.warning("Escribe una consulta primero.")
    else:
        resultado = ejecutar_agente(query)

        if resultado["top3"]:
            st.subheader("🔎 Top 3 funciones candidatas")
            for i, f in enumerate(resultado["top3"], 1):
                st.write(f"**{i}. {f['name']}** — score: `{f['score']:.3f}`")
                st.caption(f["description"])

            st.subheader("✅ Función seleccionada")
            st.success(resultado["funcion"])

        st.subheader("⚙️ Ejecución del plan")
        for linea in resultado["logs"]:
            st.write(linea)
