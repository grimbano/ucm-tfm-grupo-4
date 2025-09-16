
################################## IMPORT PACKAGES ##################################

import os
from dotenv import load_dotenv
import time
from datetime import datetime 
from typing import Any, Dict, Tuple, Union
import gradio as gr
import pandas as pd
from plotly.io import show

from src.utils.graphics import create_dashboard_from_json



############################### CREATE CONSTANT VALUES ##############################

__QUERY_BUTTON_VALUE = 'Consultar'
__NEW_QUERY_BUTTON_VALUE = 'Nueva consulta'
__EXPORT_FILE_BUTTON_VALUE = 'Exportar'


############################# LOAD ENVIRONMENT VARIABLES ############################

load_dotenv()

OUTPUT_FILES_PATH = os.getenv('OUTPUT_FILES_PATH', './output_files/query_results')


############################## DEFINE CUSTOM FUNCTIONS ##############################

if gr.NO_RELOAD:
    from src.back.graphs import get_main_graph
    main_graph = get_main_graph()

def invoke_graph(user_query: str, n_phrases: int) -> Dict[str, Any]:
    return main_graph.invoke({
        'user_query': user_query,
        'n_phrases': n_phrases,
    })


def show_results(graph_response) -> Dict:
    """
    Updates the UI components based on the data in the provided graph_response dictionary.

    This function centralizes all UI updates, setting component visibility, values,
    and content in a single step after a successful API call.

    Args:
        graph_response (Dict[str, Any]): A dictionary containing all processed
            data and UI states, typically from a previous function call.

    Returns:
        Dict[gr.Component, gr.Changeable]: A dictionary mapping Gradio components to
            their updated values or `gr.update` objects.
    """
    
    global_ok = graph_response.get('global_execution_ok')
    has_graphics = graph_response.get('graphics_json') is not None
    
    return {
        user_query_input_section: gr.update(visible=False),

        query_results_section: gr.update(visible= True),
        user_query_txt: gr.update(value= graph_response['user_query']),
        nl_conclusions_txt: gr.update(
            label= (
                'Conclusiones'
                if global_ok else
                'Respuesta'
            ),
            value= graph_response['nl_output']
        ),
        query_results_df: (
            pd.DataFrame(graph_response.get('query_results'))
        ),
        table_results_column: gr.update(visible= global_ok),
        export_options_sb: gr.update(visible= global_ok),

        graphics_tab: gr.update(visible= (
            global_ok
            and has_graphics
        )),
        graphic_plot: (
            create_dashboard_from_json(graph_response['graphics_json'], 800, None)
            if has_graphics else
            None
        ),

        sql_tab: gr.update(visible=global_ok),
        sql_query_code: gr.update(
            value= graph_response.get('sql_query'),
            lines = len((graph_response.get('sql_query') or '').strip().splitlines()) + 2,
        ),
        sql_explanation_md: gr.update(
            value= graph_response.get('sql_explanation'),
            # lines= len((graph_response.get('sql_query') or '').strip().splitlines()) - 2,
        ),
    }


def reset_new_query() -> Dict:
    """
    Resets the application's state and visibility to allow for a new query.

    This function clears the stored API response and hides the results and
    tabs, bringing the UI back to the initial query input state.

    Returns:
        Dict[gr.Component, gr.Changeable]: A dictionary mapping Gradio components
            to their updated values or visibility states.
    """
    return {
        graph_response: {},
        user_query_input_section: gr.update(visible=True),
        query_results_section: gr.update(visible=False),
        export_options_sb: gr.update(visible=False),
        file_format_dd: gr.update(value= 'CSV'),
        dowload_file_column: gr.update(visible= False),
        download_table_file: gr.update(value= None),
        graphics_tab: gr.update(visible=False),
        sql_tab: gr.update(visible=False),
    }


def hide_dowload_sidebar():
    """
    Hides the sidebar by updating its visibility to False.

    Returns:
        gr.Changeable: An update object to hide the sidebar component.
    """
    return gr.update(visible= False)


def show_dowload_sidebar_if_ok(graph_response):
    """
    Shows the sidebar only if the global_execution_ok flag is True.

    The function checks a specific key in the provided state dictionary
    to determine whether to display the sidebar. This prevents the sidebar
    from appearing prematurely if the data processing was not successful.

    Args:
        graph_response (Dict[str, Any]): The dictionary containing the
            current state of the application's data.

    Returns:
        gr.Changeable: An update object to set the sidebar's visibility.
    """

    return gr.update(visible= graph_response.get('global_execution_ok', False))


def download_data(
        query_results_df: pd.DataFrame, 
        file_format_dd: str
) -> Tuple[Union[str, Any]]:
    """
    Converts a pandas DataFrame to a CSV or Excel file and returns the file path.

    The generated filename includes a timestamp to ensure uniqueness.

    Args:
        query_results_df (pd.DataFrame): The DataFrame containing the data to be exported.
        file_format_dd (str): The desired file format, either "CSV" or "Excel".

    Returns:
        Tuple[str, gr.Changeable]: A tuple containing the path to the saved file and a
            Gradio update object to make the download link visible.
    """
    df = pd.DataFrame(query_results_df)

    # Get the current timestamp in a clean format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if file_format_dd == "CSV":
        filepath = f"{OUTPUT_FILES_PATH}_{timestamp}.csv"
        df.to_csv(filepath, index=False)

    elif file_format_dd == "Excel":
        filepath = f"{OUTPUT_FILES_PATH}_{timestamp}.xlsx"
        df.to_excel(filepath, index=False)
    
    return filepath, gr.update(visible=True)




with gr.Blocks(
    title= 'BIAI - NL-2-SQL System',
    fill_height=True,
    fill_width= True,
) as app:
    graph_response = gr.State({})

    with gr.Sidebar(
        open= False,
        visible= False,
        position= 'left',
    ) as export_options_sb:
        gr.Image(
            "./assets/logo_BIAI.png", 
            container= False,
            interactive= False,
            min_width= 0,
            show_download_button= False,
            show_share_button= False,
            show_fullscreen_button= False,
            show_label= False,
        )
        gr.Markdown('### Exportar Resultados de SQL')
        gr.Markdown('---')
        file_format_dd = gr.Dropdown(
            choices= ['CSV', 'Excel'],
            label= 'Formato de salida',
            value= 'CSV',
            interactive= True,
        )
        download_table_btn = gr.Button(
            value= __EXPORT_FILE_BUTTON_VALUE,
            variant= 'primary',
        )
        
        with gr.Column(visible= False) as dowload_file_column:
            gr.Markdown('---')
            gr.Markdown('### Descargar', )
            download_table_file = gr.File(
                label= 'Ficheros disponibles',
                visible= True,
            )


    with gr.Tab(label= '🔎 ¿Preguntas?', scale= 1) as user_query_tab:
        with gr.Column(scale=1, visible= True) as user_query_input_section:
            user_query_txt_input = gr.TextArea(
                label= 'Consulta de negocio',
                info= 'Escriba la consulta de negocio que será enviada al sistema NL-2-SQL.',
                interactive= True,
                lines= 3,
            )

            n_phrases_slider = gr.Slider(
                minimum= 5,
                maximum= 15,
                value= 10,
                step= 1,
                label= 'Cantidad de frases',
                info= 'Cantidad de frases de las que estarán compuestas las conclusiones generadas.',
                interactive= True,
            )

            query_btn = gr.Button(
                value= __QUERY_BUTTON_VALUE,
                variant= 'primary',
            )

        with gr.Column(scale= 1, visible= False) as query_results_section:
            new_query_btn = gr.Button(
                value= __NEW_QUERY_BUTTON_VALUE,
                variant= 'primary'
            )

            with gr.Row(scale= 5, visible= True):
                with gr.Column(scale= 1, visible= True) as nl_results_column:
                        user_query_txt = gr.TextArea(
                            label= 'Consulta realizada',
                            interactive= False,
                            lines= 5,
                            value= 'user_query_txt_input.value'
                        )
                        nl_conclusions_txt = gr.TextArea(
                            label= 'Conclusiones / Respuesta',
                            interactive= False,
                            lines= 20,
                        )

                with gr.Column(scale= 1, visible= False) as table_results_column:
                    query_results_df = gr.DataFrame(
                        label= 'Resultados de SQL',
                        interactive= False,
                        scale= 1,
                        wrap= True,
                        show_fullscreen_button= True,
                        show_copy_button= True,
                        show_row_numbers= True,
                        show_search= 'filter',
                    )


    with gr.Tab('📊 Gráficos', visible= False, scale= 1) as graphics_tab:
            graphic_plot = gr.Plot(
                show_label= False,
                container= False,
            )


    with gr.Tab('💻 SQL', visible= False, scale= 1) as sql_tab:
        gr.Markdown('## Explicación de la consulta SQL')
        with gr.Row(scale= 1):
            sql_query_code = gr.Code(
                value= 'SELECT * FROM resultados',
                container= True,
                scale= 3,
                interactive= False,
                language='sql-pgSQL',
                show_label= False,
            )

            with gr.Column(scale= 2):
                sql_explanation_md = gr.Markdown(
                    value= 'Explicación de la consulta SQL.',
                    show_label= False,
                    container= True,
                )      


    query_btn.click(
        fn= lambda: gr.update(
            interactive= False,
            value= 'Pensando y consultando ...',
        ),
        outputs= [query_btn]
    ).then(
        fn= invoke_graph,
        inputs= [user_query_txt_input, n_phrases_slider],
        outputs= [graph_response]
    ).then(
        fn= show_results,
        inputs= [graph_response],
        outputs=[
            user_query_input_section,
            query_results_section,
            user_query_txt,
            nl_conclusions_txt,
            query_results_df,
            table_results_column,
            export_options_sb,
            graphics_tab,
            graphic_plot,
            sql_tab,
            sql_query_code,
            sql_explanation_md,
        ]
    ).then(
        fn= lambda: gr.update(
            interactive= True,
            value= __QUERY_BUTTON_VALUE,
        ),
        outputs= [query_btn]
    )


    new_query_btn.click(
        fn= lambda: gr.update(
            interactive= False,
            value= 'Inicializando nueva consulta ...',
        ),
        outputs= [new_query_btn],
    ).then(
        fn= reset_new_query,
        inputs=[],
        outputs=[
            graph_response,
            user_query_input_section,
            query_results_section,
            export_options_sb,
            file_format_dd,
            dowload_file_column,
            download_table_file,
            graphics_tab,
            sql_tab
        ],
    ).then(
        fn= lambda: gr.update(
            interactive= True,
            value= __NEW_QUERY_BUTTON_VALUE,
        ),
        outputs= [new_query_btn],
    )


    graphics_tab.select(
        fn= hide_dowload_sidebar,
        outputs= export_options_sb
    )

    sql_tab.select(
        fn= hide_dowload_sidebar, 
        outputs= export_options_sb
    )

    user_query_tab.select(
        fn= show_dowload_sidebar_if_ok,
        inputs= graph_response,
        outputs= export_options_sb
    )


    download_table_btn.click(
        fn= lambda: gr.update(
            interactive= False,
            value= 'Exportando ...',
        ),
        outputs= [download_table_btn],
    ).then(
        fn=download_data,
        inputs= [query_results_df, file_format_dd],
        outputs= [download_table_file, dowload_file_column],
    ).then(
        fn= lambda: gr.update(
            interactive= True,
            value= __EXPORT_FILE_BUTTON_VALUE,
        ),
        outputs= [download_table_btn],
    )



if __name__ == "__main__":
    app.queue()
    app.launch(
        server_name= str(os.getenv('GRADIO_SERVER_NAME', '0.0.0.0')),
        server_port= int(os.getenv('GRADIO_SERVER_PORT', 7860)),
        favicon_path= './assets/favicon_BIAI.png',
        height= '100%',
        width= '100%',
    )