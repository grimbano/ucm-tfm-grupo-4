#################### LIBRERIAS ####################

import os
import re
from dotenv import load_dotenv 
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

import sqlglot
from sqlglot.errors import ParseError

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph


#################### IMPORTS de GASTON -> query_examples_retireval ####################

from ..embeddings import GenAIExtendedEmbeddingFunction
from ..chroma_collections import (
    ExamplesChromaCollection
)
from .states import QueryGeneratorState, QueryGeneratorOutputState


def get_query_generator_graph(model: str = 'gpt-4o') -> CompiledStateGraph[Optional[Any]]:

    #################### SETTINGS ####################
    load_dotenv()       #Cargo las variables del archivo .env

    #################### STATEs ####################
    ########## Local State ##########


    #################### TOOL QUERY EXAMPLES RETRIEVAL ####################

    # a. Model de Embeddings y coleccion de Chroma que contiene los ejemplos: **query_examples** 
    genai_embeddings = GenAIExtendedEmbeddingFunction(model= 'gemini-embedding-001')

    query_examples_collection = ExamplesChromaCollection(
        collection_name= 'query_examples',
        embedding_function= genai_embeddings,
        host= os.getenv('CHROMA_SERVER_HOST', 'localhost'),
        port= os.getenv('CHROMA_LOCAL_PORT', '8000')
    )
    #b. Definicion del esquema de entrada:
    class RetrieverInput(BaseModel):
        """
        Input schema for retriever tools. Accepts one or more queries for retrieval.
        """
        query: List[str] = Field(
            description= (
                "A list of one or more search queries to retrieve relevant information."
            )
        )
        language: Optional[str]

    ##### Definicion de la TOOL
    @tool("query_examples_retriever", args_schema=RetrieverInput)
    def get_query_examples(query: List[str], language: Optional[str] = None) -> str:
        """
        Retrieve relevant examples for the input query/queries.
        """

        def _iter_docs(search_results):
            """
            Funcion para leer correctamente lo obtenido en search_results
            """
            if not search_results:
                return []
            seq = search_results[0] if isinstance(search_results[0], list) else search_results
            for item in seq:
                doc = item[0] if isinstance(item, (tuple, list)) else item
                yield doc

        filter = None
        if language:
            filter = {'language': language}

        search_results = query_examples_collection.search(
            queries= query,
            search_type= 'similarity',
            k= 2,
            filter= filter,
        )

        if not search_results:
            return 'No semantically relevant results were found for the specified queries.'
            
        ### Si hay resultados, pintarlos bonitos para poder pasarselos al LLM:
        pretty = []
        n = 1
        for doc in _iter_docs(search_results):
            pretty.append(
                f"--- Ejemplo #{n}: ---\n"
                f"- NL: {getattr(doc, 'page_content', '')}\n"
                f"- SQL: {getattr(doc, 'metadata', {}).get('sql_query')}\n"
            )
            n += 1
        return "\n".join(pretty).strip()

    ##### Nodo que llama la TOOL:
    def node_retrieve_query_examples(state: QueryGeneratorState):
        """
        Execute tool to retrieve query examples results.

        Args:
            state (dict): The current graph state
        """
        print("---QUERY EXAMPLES RETRIEVE TOOL---")

        query = state['user_query'] 
        lang_raw = state.get("language")
        language = lang_raw.upper() if lang_raw else None
        
        LANGUAGE_DICT = {
            'SPANISH': 'ES',
            'ENGLISH': 'EN'
        }
        
        language_filter = LANGUAGE_DICT.get(language)
        
        retrieval_results = get_query_examples.invoke(input= {'query':[query], 'language':language_filter})

        return {
            'query_examples': retrieval_results
        }

    #################### TOOL VALIDACION DE SINTAXIS y READ_ONLY ####################

    # --- Sanitizador de la salida del LLM (quita ```sql, ANSI, backticks, etc.) ---
    ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

    def extract_sql(text: str) -> str:
        if not text:
            return ""
        t = ANSI_RE.sub("", text)
        t = re.sub(r"/\*[\s\S]*?\*/", "", t)
        t = re.sub(r"--.*?$", "", t, flags=re.MULTILINE)
        m = re.search(r"```(?:\s*sql)?\s*([\s\S]*?)```", t, flags=re.IGNORECASE)
        if m:
            t = m.group(1)
        t = re.sub(r"^\s*sql\s*\n", "", t, flags=re.IGNORECASE)
        m2 = re.search(r"\b(SELECT|WITH)\b", t, flags=re.IGNORECASE)
        if m2:
            t = t[m2.start():]
        t = t.strip().replace("```", "").replace("`", "")
        t = re.sub(r";\s*$", "", t)
        return t.strip()

    FORBIDDEN = (
        r"\b(INSERT|UPDATE|DELETE|MERGE|TRUNCATE|CREATE|ALTER|DROP|RENAME|REINDEX|"
        r"VACUUM|ANALYZE|CLUSTER|REFRESH|COPY|CALL|DO|GRANT|REVOKE|SET|"
        r"BEGIN|START\s+TRANSACTION|COMMIT|ROLLBACK|LOCK|UNLOCK)\b"
    )

    def basic_readonly_checks(sql: str) -> Optional[str]:
        s = sql.strip()

        # Una sola sentencia: permitimos ';' final, pero no múltiples
        if ";" in s[:-1]:
            return "Se detectaron múltiples sentencias (';'). Devuelve solo UNA consulta."

        # Debe empezar por SELECT o WITH
        if not re.match(r"^\s*(SELECT|WITH)\b", s, re.IGNORECASE):
            return "Solo se admiten consultas de lectura (SELECT/WITH)."

        # Palabras prohibidas (DML/DDL/transacciones)
        if re.search(FORBIDDEN, s, re.IGNORECASE):
            return "Se detectaron palabras no permitidas para read-only (DML/DDL/Transacción)."

        # (Opcional) Bloqueos de filas: FOR UPDATE/SHARE
        if re.search(r"\bFOR\s+(UPDATE|SHARE)\b", s, re.IGNORECASE):
            return "No se permiten bloqueos (FOR UPDATE/SHARE)."

        return None

    ##### TOOL de validacion

    @tool("query_validator")
    def query_validator(query: str, dialect: str = "postgres") -> Dict[str, Any]:
        """
        Valida que la consulta sea solo lectura y que la sintaxis sea válida usando sqlglot.
        NO se conecta a la base de datos.

        Retorna: {"ok": bool, "error": str|None}
        """
        # Extraigo la query CRUDA, sin ningun tipo de formato:
        clean = extract_sql(query)

        # Read-only (rápido, por regex)
        basic_err = basic_readonly_checks(clean)
        if basic_err:
            return {"ok": False, "error": basic_err, "sql": clean}

        # Sintaxis con sqlglot
        try:
            # parse_one garantiza una sola sentencia válida
            sqlglot.parse_one(clean, read=dialect)
            return {"ok": True, "error": None, "sql": clean}
        except ParseError as e:
            return {"ok": False, "error": f"Sintaxis inválida ({dialect}): {e}", "sql": clean}

    ########### ESQUELETO DEL GRAFO ############

    #MODELO
    llm = init_chat_model(
        model_provider= 'azure_openai',
        model= model,
        temperature= 0,
    )

    #PROMPT LLM
    def build_system_prompt(context_text: str, query_examples: str) -> str:
        return f"""Eres un generador de SQL para PostgreSQL.

    OBJETIVO:
    - Devuelve exactamente UNA sentencia de lectura (SELECT o WITH), sin explicaciones.

    REGLAS ESTRICTAS:
    - Solo lectura: empieza por SELECT o WITH.
    - Prohibido DDL/DML/transacciones/bloqueos: INSERT, UPDATE, DELETE, CREATE, DROP, ALTER,
    TRUNCATE, MERGE, COPY, CALL/EXECUTE, GRANT, REVOKE, SET, BEGIN/COMMIT/ROLLBACK, VACUUM/ANALYZE,
    FOR UPDATE/SHARE, etc.
    - Una sola sentencia. No incluyas punto y coma final.
    - Sin comentarios, ni Markdown, ni texto adicional: SALIDA = SOLO la SQL.
    - Evita SELECT *; enumera columnas necesarias.
    - Incluye ORDER BY y/o LIMIT si la intención lo requiere.
    - Literales de fecha: DATE 'YYYY-MM-DD'. Usa CAST cuando sea razonable.
    - Usa nombres de tablas/columnas que existan en el contexto. Si no están, elige alternativas plausibles y consistentes.

    CONVENCIONES:
    - Aliases claros (p. ej., revenue, total_sales, orders_count).
    - Puedes usar CTEs (WITH ...) y GROUP BY 1 si es claro.
    - Ordena por el alias de la métrica cuando aplique.
    - Preferir COALESCE para nulos en agregaciones/joins.

    Utiliza el siguiente contexto sobre: tablas, columnas y reglas de negocio:
    [CONTEXTO]
    <contexto>
    {context_text}
    </contexto>


    Utiliza los siguientes ejemplos válidos como ayuda:
    [EXAMPLES]
    <examples>
    {query_examples}
    </examples>
    """

    #USER PROMPT
    def build_user_prompt(user_query: str, last_error: Optional[str]) -> str:
        repair = (
            f"\n\nMODO REPARACIÓN:\n"
            f"- La versión anterior NO es válida.\n"
            f"- Error del validador: {last_error}\n"
            f"- Corrige la consulta para que sea sintácticamente válida en PostgreSQL y estrictamente de solo lectura."
            if last_error else ""
        )

        return f"""Genera UNA consulta SQL para PostgreSQL a partir de la intención del usuario.

    INTENCIÓN DEL USUARIO:
    {user_query}
    {repair}

    REQUISITOS ESTRICTOS:
    - SOLO una sentencia de lectura: empieza por SELECT o WITH.
    - Prohibido DML/DDL/transacciones/bloqueos: INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, TRUNCATE, MERGE, COPY, CALL/EXECUTE, GRANT, REVOKE, SET, BEGIN/COMMIT/ROLLBACK, VACUUM/ANALYZE, FOR UPDATE/SHARE, etc.
    - No múltiples sentencias ni “;” intermedio. No incluyas punto y coma al final.
    - No incluyas explicaciones, comentarios, ni Markdown. SALIDA = SOLO la SQL.
    - Evita SELECT *; enumera columnas necesarias.
    - Si el usuario pide orden o límite, incluye ORDER BY / LIMIT.
    - Usa sintaxis válida de PostgreSQL (p. ej., literales de fecha: DATE 'YYYY-MM-DD').

    FORMATO DE SALIDA (obligatorio):
    - Devuelve únicamente la SQL en texto plano, comenzando exactamente por SELECT o WITH.
    """

    ##### NODO GENERADOR #####
    def node_generate_sql(state: dict, llm) -> Dict:
        # Feedback del último error (si lo hubo) 
        last_error = None
        if state.get("valid_query_generated") is False:
            last_error = state.get("error_msg")

        # Construcción de prompts
        system = SystemMessage(content=build_system_prompt(
            state.get("context", ""),
            state.get("query_examples", "")
        ))
        user = HumanMessage(content=build_user_prompt(
            state.get("user_query", ""),
            last_error
        ))

        # Llamada al LLM con SOLO system + user
        resp = llm.invoke([system, user])  # → devuelve AIMessage
        sql_candidate = extract_sql(getattr(resp, "content", "") or "")

        # Validación de sintaxis y read_only
        dialect = state.get("dialect", "postgres")
        result = query_validator.invoke({"query": sql_candidate, "dialect": dialect})
        ok = bool(result.get("ok"))
        err = result.get("error")
        clean_sql = result.get("sql", sql_candidate)

        # Actualización del estado
        out: Dict = {
            "sql_candidate": sql_candidate or state.get("sql_candidate", ""),
            "valid_query_generated": ok,
            "error_msg": err,
            "attempt": 1,  # incrementa en cada vuelta
            "notes": [
                f"LLM generó SQL (chars={len(sql_candidate)}).",
                "Validación OK" if ok else f"Validación falló: {err}"
            ]
        }

        # Si pasó la validación, fijamos la final
        if ok:
            out["sql_query"] = clean_sql

        return out


    ##### ROUTER Y NODOS FINALES ######

    def router(state: dict) -> str:
        ok = state.get("valid_query_generated")
        attempts = state.get("attempt", 0)
        max_attempts = state.get("max_attempts", 1)

        if ok is True:
            return "success"
        if attempts >= max_attempts:
            return "fail"
        return "retry"


    ####### CONSTRUCCION DEL SUBGRAFO #########
    def build_subgraph_query_generator(llm):
        graph = StateGraph(
            state_schema= QueryGeneratorState,
            input_schema= QueryGeneratorState,
            output_schema= QueryGeneratorOutputState
        )

        graph.add_node("query_examples_retriever", node_retrieve_query_examples)
        graph.add_node("query_generator", lambda s: node_generate_sql(s, llm))

        graph.add_edge(START, "query_examples_retriever")
        graph.add_edge("query_examples_retriever", "query_generator")

        graph.add_conditional_edges(
            "query_generator",
            router,
            {
                "retry": "query_generator",          # vuelve a generarse (auto-realimentación)
                "success": END,       # fija final_sql
                "fail": END,          # termina con error
            },
        )

        return graph.compile()

    app = build_subgraph_query_generator(llm)



    return app

