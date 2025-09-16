
#################### LIBRERIAS ####################

from dotenv import load_dotenv 
from typing import Optional, Any
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, START, END

from ...utils.doc_generators import convert_to_markdown_table
from ...utils.graphics import create_dashboard_from_json
from .states import ConclusionsGeneratorState, ConclusionsGeneratorOutputState

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_conclusions_generator_graph(
        n_phrases: int = 10, 
        max_retries: int = 5
) -> CompiledStateGraph[Optional[Any]]:

    # Nos aseguramos de cargar las variables de entorno
    load_dotenv()
    
    # Definimos los modelos a utilizar
    llm_generator = init_chat_model(
        model_provider= 'azure_openai',
        model= 'gpt-4.1-mini',
        temperature= 0.10,
    )

    llm_graphics_generator = init_chat_model(
        model_provider= 'azure_openai',
        model= 'gpt-4.1-mini',
        temperature= 0.75,
    )


    # Definimos agentes presentes en el sistema

    ## NL CONCLUSIONS GENERATOR
    nl_conclusions_prompt = ChatPromptTemplate.from_messages([{
        "role": "system",
        "content": (
            "Eres un analista experto en el dominio de la base de datos consultada."
            "\n\nLa consulta realizada por un usuario de negocio es:"
            "\n\n{user_query}"
            "\n\nLa salida en texto plano (markdown) de la consulta SQL ejecutada es:"
            "\n\n{query_results}"
            "\n\n\nTu tarea es extraer las conclusiones principales de los datos, redactadas de "
            "forma breve y directa, sin explicaciones innecesarias ni contexto adicional."
            "\nDirígete a un usuario de negocio con conocimientos en el tema, "
            "por lo que no es necesario definir conceptos básicos."
            "\nMáximo {n_phrases} frases concisas pero, usando terminología técnica del dominio cuando corresponda."
            "\nNo incluyas datos sin relevancia ni interpretaciones especulativas."
            "\nLa respuesta debe estar en el siguiente idioma: {language}"
        )
    }])

    nl_conclusions_generator = nl_conclusions_prompt | llm_generator


    ## NL SQL EXPLANATION GENERATOR
    nl_sql_explanaition_prompt = ChatPromptTemplate.from_messages([{
        "role": "system",
        "content": (
            "Eres un analista de datos experimentado, especialista en el dominio de negocio "
            "relacionado con la base de datos que se te consulta. Tu tarea es analizar la "
            "consulta SQL ejecutada y explicar la lógica que subyace a la misma, para que "
            "un usuario de negocio pueda entender cómo se llegó a la respuesta a su pregunta."
            "\n\nLa consulta del usuario de negocio es:"
            "\n\n{user_query}"
            "\n\nLa consulta SQL que se ejecutó para responderla es:"
            "\n\n{sql_query}"
            "\n\n\nTu respuesta debe ser un análisis conciso y directo, sin jerga innecesaria. "
            "Dirígete al usuario como si estuvieras explicando tu proceso de pensamiento."
            "\n\nSigue este formato:"
            "\n\n## Análisis de la Lógica de la Consulta"
            "\n\nExplica en un párrafo la lógica principal de la consulta. Describe cómo se "
            "combinan las tablas y qué filtros se aplican para obtener los datos relevantes."
            "\n\n## Conclusión y Resultados Clave"
            "\n\nProporciona las conclusiones principales de los datos, basándote en la "
            "lógica de la consulta. Si no se han pasado los resultados, limita tu respuesta a "
            "una explicación de qué tipo de información se obtendría. No especules sobre los "
            "valores exactos."
            "\n\nUtiliza un máximo de dos párrafos en total. Usa terminología técnica del "
            "dominio solo cuando sea estrictamente necesario para la claridad. No incluyas "
            "información irrelevante ni interpretaciones especulativas."
            "\n\nLa respuesta debe estar en el siguiente idioma: {language}"
        )
    }])

    nl_sql_explanation_generator = nl_sql_explanaition_prompt | llm_generator


    ## GRAPHICS GENERATOR
    graphics_generator_prompt = ChatPromptTemplate.from_messages([{
        "role": "system",
        "content": (
            "Eres un consultor experto en análisis de negocios y un maestro en la visualización de datos. Tu misión es transformar datos brutos en una narrativa visual coherente y estratégica, a través de un dashboard empresarial de 4 gráficos. "
            "Tu trabajo va más allá de la simple representación: cada gráfico debe ser un insight único que, en conjunto, cuente una historia completa y sin redundancia sobre los resultados de la consulta. "
            "Debes mantener una visión global de cómo los 4 gráficos se complementan entre sí para responder a diferentes facetas de la consulta del usuario."
            "La salida debe ser un único JSON válido, conteniendo el título del dashboard y una lista de 4 diccionarios de Plotly. "
            "Todo el texto del dashboard (títulos, etiquetas, descripciones, etc.) debe estar en el idioma definido por la variable '{language}'."
            "\n\nContexto de la consulta de negocio:"
            "\n\n{user_query}"
            "\n\nResultados de la consulta SQL:"
            "\n\n{query_results}"
            "\n\n**Estrategia de Visualización Creativa y Analítica:**"
            "\n- **Enfoque de la narrativa:** Cada gráfico debe abordar una faceta diferente del análisis. Combina tipos de gráficos de forma inteligente para guiar al usuario a través de un descubrimiento de datos. Por ejemplo, inicia con una visión general, luego muestra la evolución temporal, sigue con una comparación de rendimiento, y finaliza con la relación entre dos métricas clave."
            "\n- **Diversidad y sinergia:** Elige 4 tipos de gráficos distintos de la siguiente lista: barras (bar), líneas (line), tarta (pie), dispersión (scatter) e histogramas (histogram). La selección debe ser deliberada para potenciar la narrativa de los datos. Evita cualquier repetición de información entre gráficos."
            "\n- **Claridad en gráficos complejos:**"
            "\n    - **Gráficos de Tarta (Pie Charts):** Solo utiliza un gráfico de tarta si hay **5 o menos categorías principales**. Si el número de elementos es mayor, agrupa los adicionales en una categoría única llamada 'Otros' para mantener la claridad y la legibilidad."
            "\n    - **Gráficos de Líneas y Dispersión (line y scatter):** Es **imperativo y obligatorio** que estos gráficos muestren múltiples trazas. Cada traza debe corresponder a una categoría o grupo distinto, permitiendo un análisis comparativo y detallado dentro del mismo gráfico. **Evita usar estos gráficos si la serie de datos es demasiado corta (menos de 3 puntos).**"
            "\n- **Profesionalismo y prohibiciones:** Mantén una estética empresarial impecable. Los títulos, etiquetas y colores deben ser coherentes y profesionales. **Bajo ninguna circunstancia debes generar mapas de calor (heatmaps), ya que no son parte de este conjunto de visualizaciones.**"
            "\n\n**Directrices de Formato y Salida (Extremadamente Estrictas):**"
            "\n- **La salida debe ser ÚNICAMENTE el JSON COMPLETO y VÁLIDO.**"
            "\n- **TIENES PROHIBIDO ABSOLUTAMENTE incluir cualquier tipo de texto, explicación, preámbulo, comentarios, o formato adicional (como Markdown, bloques de código, etc.).**"
            "\n- **El JSON debe empezar con `{{` y terminar con `}}`.**"
            "\n- **Asegura que cada par clave-valor esté separado por una coma (`,`) correcta.**"
            "\n- **No debe haber comas adicionales después del último elemento de una lista o diccionario.**"
            "\n- **Utiliza siempre comillas dobles (`\"`) para las claves y los valores de texto.**"
            "\n- **Si se requiere una suma o cualquier otro cálculo, realiza la operación tú mismo y coloca el valor numérico final directamente en el JSON.** **No incluyas expresiones matemáticas ni sumas dentro de los arrays.** Por ejemplo, en lugar de `[10, 20+5, 30]`, escribe `[10, 25, 30]`."
            "\n\n**Ejemplo del formato JSON requerido:**"
            "\n\n{{\n"
            " \"dashboard_title\": \"Título Conciso del Dashboard\",\n"
            " \"charts\": [\n"
            "  {{\n"
            "   \"data\": [...],\n"
            "   \"layout\": {{\n"
            "    \"title\": \"Título del Gráfico 1\",\n"
            "    \"xaxis\": {{\"title\": \"Eje X\"}},\n"
            "    \"yaxis\": {{\"title\": \"Eje Y\"}},\n"
            "    \"plot_bgcolor\": \"#f2f2f2\",\n"
            "    \"paper_bgcolor\": \"#ffffff\"\n"
            "   }}\n"
            "  }},\n"
            "  ...\n"
            " ]\n"
            "}}\n"
        )
    }])

    graphics_generator = graphics_generator_prompt | llm_graphics_generator



    # Definimos nodos

    def nl_conclusions_generation_node(state: ConclusionsGeneratorState):
        """
        Nodo que analiza los resultados de la consulta SQL y genera 
        conclusiones relevantes para la consulta del usuario.
        """
        logging.info("--- INICIANDO GENERACIÓN DE CONCLUSIONES 📝 ---")
        user_query = state['user_query']
        _n_phrases = state.get('n_phrases', n_phrases)
        language = state['language']
        query_results = state['query_results']

        nl_output = nl_conclusions_generator.invoke({
            'user_query': user_query,
            'language': language,
            'query_results': convert_to_markdown_table(query_results),
            'n_phrases': _n_phrases,
        }).content
        
        return {"nl_output": nl_output}


    def sql_query_explanation_node(state: ConclusionsGeneratorState):
        """
        Nodo que analiza la consulta SQL frente a la consulta del 
        usuario y genera una breve explicación de lo desarrollado.
        """
        logging.info("--- INICIANDO EXPLICACIÓN DE CONSULTA SQL 🗂️ ---")
        user_query = state['user_query']
        language = state['language']
        sql_query = state['sql_query']

        sql_explanation = nl_sql_explanation_generator.invoke({
            'user_query': user_query,
            'language': language,
            'sql_query': sql_query,
        }).content
        
        return {"sql_explanation": sql_explanation}


    def graphs_generation_node(state: ConclusionsGeneratorState) -> dict:
        """
        Nodo que genera gráficos basados en los resultados de la consulta SQL, 
        que sean relevantes para la consulta del usuario.
        """
        logging.info("--- INICIANDO GENERACIÓN DE GRÁFICOS 📊 ---")
        user_query = state['user_query']
        language = state['language']
        query_results = state['query_results']
        graphs_retries = state.get('graphs_retries', 0) + 1
        
        graphics_json = graphics_generator.invoke({
            'user_query': user_query,
            'language': language,
            'query_results': convert_to_markdown_table(query_results),
        }).content

        if create_dashboard_from_json(graphics_json) is None:
            logging.error("--- ❌ Error al generar gráficos ---")
            return {
                "graphics_json": None,
                "graphs_retries": graphs_retries
            }

        return {"graphics_json": graphics_json}
    


    # Definimos el grafo
    workflow = StateGraph(
        state_schema= ConclusionsGeneratorState,
        input_schema= ConclusionsGeneratorState,
        output_schema= ConclusionsGeneratorOutputState,
    )

    workflow.add_node('generate_nl_conclusions', nl_conclusions_generation_node)
    workflow.add_node('generate_sql_explanation', sql_query_explanation_node)
    workflow.add_node('generate_plotly_graphs', graphs_generation_node)

    workflow.add_edge(START, 'generate_nl_conclusions')
    workflow.add_edge(START, 'generate_sql_explanation')
    workflow.add_edge('generate_nl_conclusions', 'generate_plotly_graphs')
    workflow.add_edge('generate_sql_explanation', 'generate_plotly_graphs')
    workflow.add_conditional_edges(
        'generate_plotly_graphs',
        lambda state: (
            'retry'
            if state.get('graphics_json') is None
            and state.get('graphs_retries', 0) < max_retries
            else 'continue'
        ),
        {
            'retry': 'generate_plotly_graphs',
            'continue': END
        }
    )

    compiled_graph = workflow.compile()


    # Devolvemos el grafo compilado

    return compiled_graph

