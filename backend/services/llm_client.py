# from typing import List

# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_community.chat_models import ChatOllama

# # Initialize Ollama Chat Model
# # Ensure you have 'llama3' or another model pulled via `ollama pull <model_name>`
# llm = ChatOllama(model="llama3", temperature=0) # Adjust model and temperature as needed

# async def get_chat_response(query: str, context_chunks: List[str]) -> str:
#     """
#     Generates a response from the local LLM using the provided query and context.
#     """
#     if context_chunks:
#         context = "\n".join(context_chunks)
#         prompt_template = ChatPromptTemplate.from_messages(
#             [
#                 ("system", "You are a helpful AI assistant. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know."),
#                 ("user", "Context: {context}\n\nQuestion: {question}"),
#             ]
#         )
#         chain = prompt_template | llm | StrOutputParser()
#         response = await chain.ainvoke({"context": context, "question": query})
#     else:
#         # Fallback if no context is provided
#         prompt_template = ChatPromptTemplate.from_messages(
#             [
#                 ("system", "You are a helpful AI assistant."),
#                 ("user", "{question}"),
#             ]
#         )
#         chain = prompt_template | llm | StrOutputParser()
#         response = await chain.ainvoke({"question": query})

#     return response




from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from .llm_factory import get_llm

async def get_chat_response(query: str, context_chunks: list[str], chat_history: list = None) -> str:
    llm = get_llm()
    
    if chat_history is None:
        chat_history = []
    
    if not context_chunks:
        return "I don't have any relevant information in the provided documents to answer this question. Please make sure you've uploaded the relevant documents."
    
    system_prompt = (
        "You are a precise document assistant. Follow these rules strictly:\n"
        "1. ONLY use information from the CONTEXT provided below\n"
        "2. DO NOT use any external knowledge or internet information\n"
        "3. If the answer is not in the context, say 'I cannot find this information in the provided documents'\n"
        "4. Be specific and cite relevant parts of the context\n"
        "5. If data can be presented as a table, format it using markdown table syntax\n"
        "6. Always provide complete and accurate information from the context\n\n"
        "CONTEXT:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    context_text = "\n\n---\n\n".join(context_chunks)
    
    history_messages = []
    for msg in chat_history[-6:]:
        if msg['role'] == 'user':
            history_messages.append(HumanMessage(content=msg['content']))
        else:
            history_messages.append(AIMessage(content=msg['content']))
    
    return await chain.ainvoke({
        "context": context_text, 
        "question": query,
        "chat_history": history_messages
    })