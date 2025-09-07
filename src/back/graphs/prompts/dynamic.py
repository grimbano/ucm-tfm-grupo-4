

_RETRIEVAL_GRADER_DYNAMIC_PROMPT_DICT = {
    'business_logic': {
        'user_query': 'Business Rules related to: ',
        'output': (
            "Your final output should be a single, structured text that begins with the heading 'Synthesized Business Logic'. "
            "Start with a brief, high-level summary. "
            "Follow with a detailed breakdown of each business rule or concept from the context, using clear headings or bullet points. "
            "**Crucially, identify and extract any SQL expressions, code snippets, or fragments** that are used to define temporal calculations "
            "(e.g., 'mes pasado', 'Year to Date') or other business rules. **Include these exact SQL fragments directly within your detailed breakdown.**"
        )
    },
    'mdl': {
        'user_query': 'Tables summaries (including their keys) and columns needed to responds: ',
        'output': (
            "Your final output should be a single, structured text with two main sections:"
            "1. A detailed summary of all relevant **databases, schemas**, tables, and columns for the query."
            "2. A summary of how to relate these tables, with the option to propose **SQL join conditions** as fragments."
            "3. You are **ABSOLUTELY FORBIDDEN FROM INVENTING, EXTRACTING, OR SUGGESTING any new SQL query or complete SQL code** not "
            "provided in the source material. You may only provide relevant fragments or logical components of SQL that are directly "
            "derived from the table and join information provided in the context."
        )
    }
}

