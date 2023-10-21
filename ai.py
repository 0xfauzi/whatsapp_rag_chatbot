from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from decouple import config
from langchain.text_splitter import CharacterTextSplitter


def chunk_text(text):
    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_embeddings(text_chunks):
    embeddings = OpenAIEmbeddings(
        openai_api_key=config("OPENAI_API_KEY")
    )
    
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(embeddings):
    llm = ChatOpenAI(
        openai_api_key=config("OPENAI_API_KEY")
    )

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True
    )

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=embeddings.as_retriever(),
        memory=memory,
        verbose=True,
    )
    return conversation_chain