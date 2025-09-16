
import json
import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_dashboard_from_json(
        json_str: str,
        height: int = 900,
        width: int = 1600,
    ) -> None | go.Figure:
    """
    Procesa un JSON de gráficos y crea un dashboard interactivo de Plotly.

    Args:
        json_str: Una cadena JSON válida que contiene el título del dashboard
                y una lista de diccionarios de Plotly.
        height: Alto total del conjunto de gráficos.
        width: Ancho total del conjunto de gráficos.
    """
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    if not json_str:
        logging.info("No hay datos de gráficos para procesar. Saliendo.")
        return None

    _json_str = json_str
    if json_str.strip().lower().startswith('```json'):
        _json_str= json_str.strip()[len('```json'):]

    if json_str.strip().endswith('```'):
        _json_str= json_str.strip()[:-len('```')]

    try:
        data = json.loads(_json_str)
        main_title = data.get('dashboard_title', 'Dashboard de Análisis')
        json_graphs = data.get('charts', [])
    except json.JSONDecodeError as e:
        logging.error(f"Error al decodificar el JSON: {e}")
        return None

    if not json_graphs:
        logging.info("No hay datos de gráficos para procesar. Saliendo.")
        return None

    subplot_titles = []
    specs = []
    row_specs = []

    for graph in json_graphs:
        title_obj = graph['layout'].get('title', "Sin Título")
        if isinstance(title_obj, dict):
            title = title_obj.get('text', "Sin Título")
        else:
            title = title_obj
        subplot_titles.append(title)
        
        graph_data = graph['data']
        if isinstance(graph_data, dict):
            graph_data = [graph_data]
            
        is_domain_chart = graph_data[0]['type'] in ['pie', 'funnelarea', 'sunburst', 'treemap']
        row_specs.append({"type": "domain"} if is_domain_chart else {"type": "xy"})
        
        if len(row_specs) == 2:
            specs.append(row_specs)
            row_specs = []
    
    if len(specs) < 2 and len(json_graphs) > 2:
        while len(specs) < 2:
            specs.append([{}, {}])
    
    if len(specs) == 0:
        specs = [[{}, {}], [{}, {}]]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=subplot_titles,
        specs=specs
    )

    row = 1
    col = 1
    for i, graph in enumerate(json_graphs):
        graph_data = graph['data']
        if isinstance(graph_data, dict):
            graph_data = [graph_data]
        
        for trace_dict in graph_data:
            trace_type = trace_dict.get('type')

            if trace_type == 'pie':
                fig.add_trace(go.Pie(trace_dict), row=row, col=col)
                break
            elif trace_type == 'bar':
                fig.add_trace(go.Bar(trace_dict), row=row, col=col)
                break
            elif trace_type == 'scatter':
                fig.add_trace(go.Scatter(trace_dict), row=row, col=col)
                break
            elif trace_type == 'line':
                fig.add_trace(go.Scatter(trace_dict), row=row, col=col)
                break
            elif trace_type == 'heatmap':
                fig.add_trace(go.Heatmap(trace_dict), row=row, col=col)
                break
            elif trace_type == 'histogram':
                fig.add_trace(go.Histogram(trace_dict), row=row, col=col)
                break
            else:
                logging.warning(f"Tipo de gráfico desconocido: '{trace_type}'. Omitiendo traza en la posición ({row},{col}).")
                

        subplot_layout = graph.get('layout', {})
        
        xaxis_title = subplot_layout.get('xaxis', {}).get('title', {})
        if isinstance(xaxis_title, dict):
            xaxis_title_text = xaxis_title.get('text')
        else:
            xaxis_title_text = xaxis_title
            
        yaxis_title = subplot_layout.get('yaxis', {}).get('title', {})
        if isinstance(yaxis_title, dict):
            yaxis_title_text = yaxis_title.get('text')
        else:
            yaxis_title_text = yaxis_title
            
        fig.update_xaxes(title_text=xaxis_title_text, row=row, col=col)
        fig.update_yaxes(title_text=yaxis_title_text, row=row, col=col)
        
        col += 1
        if col > 2:
            col = 1
            row += 1
            
    fig.update_layout(
        height= height,
        width= width,
        autosize= True,
        title_text= main_title,
        title_x= 0.5,
        font=dict(
            family= "Arial, sans-serif",
            size= 12
        ),
        paper_bgcolor="#f2f2f2",
        plot_bgcolor="#ffffff",
        margin=dict(l=50, r=50, t=80, b=50),
    )

    return fig
