
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

llm_graders = init_chat_model(
    model_provider= 'azure_openai',
    model= 'gpt-4o-mini',
    temperature= 0,
    max_tokens= 1000
)

llm_classifiers = init_chat_model(
    model_provider= 'azure_openai',
    model= 'gpt-4o-mini',
    temperature= 0,
    max_tokens= 1000
)

llm_retrievals = init_chat_model(
    model_provider= 'azure_openai',
    model= 'gpt-4o-mini',
    temperature= 0,
    max_tokens= 1000
)

llm_generators = init_chat_model(
    model_provider= 'azure_openai',
    model= 'gpt-4.1',
    temperature= 0,
    max_tokens= 2000
)

