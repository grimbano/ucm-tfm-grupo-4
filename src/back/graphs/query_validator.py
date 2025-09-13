
#################### LIBRERIAS ####################

from dotenv import load_dotenv 
from typing import Optional, Any
from sqlalchemy import create_engine, text
from langchain_community.utilities import SQLDatabase
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, START, END


from config import get_pg_config
from .states import QueryValidatorState, QueryValidatorOutputState
from .pydantic_models import TablesExtractionResult, QueryCoherenceGraderResult


def get_query_validator_graph(max_retries: int = 5) -> CompiledStateGraph[Optional[Any]]:

    # Nos aseguramos de cargar las variables de entorno
    load_dotenv()
    
    # Definimos los modelos a utilizar
    llm_structured_outputs = init_chat_model(
        model_provider= 'azure_openai',
        model= 'gpt-4o-mini',
        temperature= 0,
        max_tokens= 1000
    )

    llm_query_corrector = init_chat_model(
        model_provider= 'azure_openai',
        model= 'gpt-4.1',
        temperature= 0,
        max_tokens=2048
    )


    # Definimos agentes presentes en el sistema

    ## TABLES EXTRACTOR
    tables_extractor_prompt = ChatPromptTemplate.from_messages([
        {
            "role": "system", 
            "content": (
                "Eres un asistente experto en SQL. Tu única tarea es extraer **solamente los nombres de las tablas** de una consulta SQL."
                "\n\n**Reglas clave:**"
                "\n1.  **Ignora CTEs**: No extraigas los nombres de las CTEs (Common Table Expressions) que se definen con `WITH`."
                "\n2.  **Solo nombres de tablas con esquema**: Identifica y extrae únicamente los nombres de tablas que vengan precedidos por un esquema. Por ejemplo, en `mi_esquema.mi_tabla`, solo debes devolver `mi_tabla`."
                "\n3.  **Formato de salida**: Devuelve los nombres de las tablas sin el esquema, separados por comas y sin ningún otro texto ni caracteres extraños."
                "\n\n**Ejemplo de salida esperada:**"
                "\n`['dim_customer', 'fact_sales']`"
            )
        },
        {"role": "user", "content": "Extrae los nombres de tabla de la siguiente query: '{sql_query}'"}
    ])

    tables_extractor = tables_extractor_prompt | llm_structured_outputs.with_structured_output(TablesExtractionResult)


    ## COHERENCE GRADER
    coherence_grader_prompt = ChatPromptTemplate.from_messages([
        {"role": "system", "content": "Eres un juez experto en SQL y vas a recibir un mensaje de usuario, una query y un resumen en alto nivel de las tablas involucradas en la query. Responde SÓLO con 'COHERENTE' si la query es correcta para el mensaje, o con 'INCOHERENTE'."},
        {"role": "user", "content": "Mensaje del usuario: '{user_query}'\nQuery SQL: '{sql_query}'\nResumen de alto nivel: '{context}'"}
    ])

    coherence_grader = coherence_grader_prompt | llm_structured_outputs.with_structured_output(QueryCoherenceGraderResult)


    ## QUERY CORRECTOR
    DYNAMIC_PROMPT_CONTENT = {
        'error_coherence': """
        Corrige la siguiente query SQL para que sea coherente con el mensaje del usuario. 
        Asegúrate de incluir el nombre del esquema para cada tabla real.
        No añadas un esquema a los nombres de las CTEs (WITH).
        
        ---

        Mensaje del usuario:
        <user_query>
        {user_query}
        </user_query>

        ---

        Query original:
        <original_sql_query>
        {original_sql_query}
        </original_sql_query>

        ---

        Resumen de tablas:
        <context>
        {context}
        </context>
        """,
        
        'error_db': """
        Tu tarea es corregir una consulta SQL que ha fallado. Analiza cuidadosamente el **mensaje de error** proporcionado para identificar la causa raíz del fallo.
        
        **Proceso de corrección:**

        1.  **Reflexiona sobre el error:** Lee y comprende el mensaje de error. Considera qué parte de la query está causando el problema.
        2.  **Consulta la información:** Utiliza el `user_query`, la `original_sql_query` y el `tables_info` para contextualizar el problema.
        3.  **Identifica la tabla:** Asegúrate de que todas las tablas reales en la query incluyan su esquema (`<schema>.<tabla>`). \
            Recuerda que las CTEs (WITH) no pertenecen a ningún esquema y no deben ser modificadas.

        ---

        Mensaje del usuario:
        <user_query>
        {user_query}
        </user_query>

        ---

        Query original:
        <original_sql_query>
        {original_sql_query}
        </original_sql_query>

        ---

        Error al ejecutar query:
        <error_msg>
        {error_msg}
        </error_msg>

        ---

        Resumen de tablas:
        <tables_info>
        {tables_info}
        </tables_info>
        """
    }

    query_corrector_prompt = ChatPromptTemplate.from_messages([
        {"role": "system", "content": "Eres un experto en bases de datos. Devuelve SÓLO la query corregida, sin usar MARKDOWN, sin explicaciones ni texto adicional.\n\n{prompt_content}"},
        # {"role": "user", "content": '{prompt_content}'}
    ])

    query_corrector = query_corrector_prompt | llm_query_corrector




    # Definimos nodos

    def check_db_connection_node(state: QueryValidatorState):
        print("\n--- INICIANDO COMPROBACIÓN DE CONEXIÓN A BBDD ⚙️ ---")

        db_name = state['db_name']
        schema_name = state['schema_name']

        try:
            db_uri = get_pg_config(database_name= db_name).get_db_uri(schema_name)

            db = {
                'table_info': SQLDatabase.from_uri(db_uri),
                'engine': create_engine(db_uri)
            }

            print("✅ Conexión a la base de datos establecida correctamente.")

            return {'db': db}

        except Exception as e:
            print(f"❌ Error al conectar a la base de datos: {e}")
            return {
                'valid_query_execution': False,
                'db': None
            }


    def table_name_extraction_node(state: QueryValidatorState):
        print("\n--- INICIANDO FASE DE EXTRACCIÓN DE TABLAS CON LLM 🧮 ---")

        sql_query = state['sql_query']
        
        table_names = tables_extractor.invoke({'sql_query': sql_query}).table_names
        print(f"Tablas detectadas por el LLM: {table_names}")
        return {"table_names": table_names}


    def coherence_grading_node(state: QueryValidatorState):
        user_query = state['user_query']
        context = state['context']
        sql_query = state['sql_query']
        db = state['db']
        table_names = state['table_names']
        retries = state.get('retries', 0) + 1
        
        if retries > max_retries:
            print(f"\n❌🔚 Límite de {max_retries} reintentos alcanzado. Finalizando.")
            return {
                'valid_query_execution': False,
                "query_validation_error_type": "limit_reached"
            }

        print("\n--- INICIANDO FASE DE JUEZ DE COHERENCIA 👩‍⚖️ ---\n")

        coherent = coherence_grader.invoke({
            'user_query': user_query,
            'context': context,
            'sql_query': sql_query,
        }).coherent

        print(f"--- Veredicto del juez: {'COHERENTE ✅' if coherent else 'INCOHERENTE ❌'} ---")
        
        if not coherent:
            print("\n❌ La query es incoherente. No se ejecutará en la BBDD.")
            return {
                "query_validation_error_type": "error_coherence", 
                "retries": retries
            }
        
        print("\n--- PASANDO A FASE DE EJECUCIÓN EN POSTGRESQL ---\n")

        try:
            # Usamos la lista de tablas que nos ha dado el extractor
            tables_info = [db['table_info'].get_table_info([table]) for table in table_names]

            with db['engine'].connect() as conn:
                result = conn.execute(text(sql_query))
                query_results = [row for row in result.mappings()]

            
            print(f"--- ✅ Query ejecutada correctamente. ---")
            return {
                "tables_info": tables_info,
                "query_results": query_results,
                "valid_query_execution": True
            }

        except Exception as e:
            print(f"\n❌ Error de PostgreSQL detectado: {e}\n")
            return {
                "query_validation_error_type": "error_db",
                "query_validation_error_msg": e,
                "retries": retries
            }


    def query_correction_node(state: QueryValidatorState):
        user_query = state['user_query']
        context = state['context']
        tables_info = state.get('tables_info', context)
        original_sql_query = state['sql_query']
        error_type = state['query_validation_error_type']
        error_msg = state.get('query_validation_error_msg')

        prompt_content = DYNAMIC_PROMPT_CONTENT.get(error_type, 'N/A')

        if prompt_content == 'N/A':
            print("--- ❌ Error no reconocido. Saliendo del corrector. ---")
            return {"sql_query": original_sql_query}
        
        print("\n--- INICIANDO FASE DE CORRECIÓN 📝 ---\n")
        corrected_query = query_corrector.invoke({
            'prompt_content': prompt_content.format(
                user_query= user_query,
                error_msg= error_msg,
                tables_info= tables_info,
                context= context,
                original_sql_query= original_sql_query,
            )
        }).content
            
        print(f"✅  > Query corregida recibida: {corrected_query[:70]}...")
        
        return {"sql_query": corrected_query}
    


    # Definimos el grafo
    workflow = StateGraph(
        state_schema= QueryValidatorState,
        input_schema= QueryValidatorState,
        output_schema= QueryValidatorOutputState
    )

    workflow.add_node(
        'check_db_connection',
        check_db_connection_node
    )
    workflow.add_node(
        'tables_extraction',
        table_name_extraction_node
    )
    workflow.add_node(
        'validation',
        coherence_grading_node
    )
    workflow.add_node(
        'query_correction',
        query_correction_node
    )

    workflow.add_edge(START, 'check_db_connection')
    workflow.add_conditional_edges(
        'check_db_connection',
        lambda state: 'abort' if state['db'] is None else 'continue',
        {
            'abort': END,
            'continue': 'tables_extraction'
        }
    )
    workflow.add_edge('tables_extraction', 'validation')
    workflow.add_conditional_edges(
        'validation',
        lambda state: 'correct' if state.get('valid_query_execution') is None else 'end',
        {
            'correct': 'query_correction',
            'end': END
        }
    )
    workflow.add_edge('query_correction', 'tables_extraction')

    compiled_graph = workflow.compile()


    # Devolvemos el grafo compilado

    return compiled_graph

