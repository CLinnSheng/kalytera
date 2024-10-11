from langchain_community.document_loaders import PyPDFLoader
from langchain_google_vertexai import ChatVertexAI
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from typing import List
from enum import Enum
import logging
import os


class LLMProvider(Enum):
    GEMINI = 1
    OLLAMA = 2

class SplitStrategy(Enum):
    RECURSIVE_TEXT_SPLITTER = 1
    SEMANTIC = 2


class ChainType(Enum):
    STUFF = 1
    REFINE = 2


class RAGSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGSingleton, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self, persist_directory="chroma"):
        logging.debug("Initializing RAG")
        self.llm = None
        self.vectorstore = None
        self.retriever = None
        self.rag_chain = None
        self.embeddings = self.initialize_embeddings(provider=LLMProvider.GEMINI)
        self.persist_directory = persist_directory

    def load_pdf(self, file_path):
        logging.debug(f"Loading PDF: {file_path}")
        loader = PyPDFLoader(file_path)
        return loader.load()

    def load_pdfs_from_directory(self, directory_path):
        logging.debug(f"Loading PDFs from directory: {directory_path}")
        pdfs: List[Document] = []
        for filename in os.listdir(directory_path):
            if not filename.endswith(".pdf"):
                continue

            file_path = os.path.join(directory_path, filename)
            pdf = self.load_pdf(file_path)
            pdfs.extend(pdf)
        return pdfs

    def initialize_llm(self, provider: LLMProvider = LLMProvider.OLLAMA, **kwargs):
        logging.debug("Initializing LLM")
        if provider == LLMProvider.GEMINI:    
            self.llm = ChatVertexAI(
                model="gemini-1.5-flash",
                temperature=0,
                project=kwargs["project"]
            )
        elif provider == LLMProvider.OLLAMA:
            if "ollama_url" not in kwargs:
                kwargs["ollama_url"] = os.environ["OLLAMA_URL"]
            self.llm = ChatOllama(
                model="llama3.1",
                temperature=0,
                base_url=kwargs["ollama_url"]
            )

    def initialize_embeddings(self,
                              provider: LLMProvider = LLMProvider.OLLAMA, 
                              hf_token = None, 
                              model_name = "sentence-transformers/all-MiniLM-l6-v2",
                              **kwargs):
        logging.debug("Initializing embeddings")

        if provider == LLMProvider.OLLAMA:
            if "ollama_url" not in kwargs:
                kwargs["ollama_url"] = os.environ["OLLAMA_URL"]
            return OllamaEmbeddings(model="nomic-embed-text", base_url=kwargs["ollama_url"])
        elif provider == LLMProvider.GEMINI:
            if hf_token is None:
                hf_token = os.environ["HUGGINGFACE_API_KEY"]
                
            return HuggingFaceInferenceAPIEmbeddings(
                api_key=hf_token, model_name=model_name
            )

    def initialize_vectorstore(self):
        logging.debug("Initializing vectorstore")
        if self.vectorstore is None:
            raise ValueError(
                "Vectorstore not initialized. Call create_vectorstore() first.")

        return self.vectorstore

    def split_documents(self,
                        docs: List[Document],
                        chunk_size=1000, chunk_overlap=200,
                        split_strategy: SplitStrategy = SplitStrategy.RECURSIVE_TEXT_SPLITTER
                        ) -> List[Document]:
        splits: List[Document] = []

        if split_strategy == SplitStrategy.RECURSIVE_TEXT_SPLITTER:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            splits = text_splitter.split_documents(docs)
        elif split_strategy == SplitStrategy.SEMANTIC:
            text_splitter = SemanticChunker(
                # self.embeddings, breakpoint_threshold_type="percentile"
                self.embeddings, breakpoint_threshold_type="standard_deviation"
                # self.embeddings, breakpoint_threshold_type="gradient"
            )
            splits = text_splitter.split_documents(docs)

        for split in splits:
            logging.debug(split.metadata)

        logging.info(f"Number of splits: {len(splits)}")
        return splits

    def create_vectorstore(self, docs: List[Document], should_create=True):
        logging.debug("Creating vectorstore")

        if not should_create:
            self.vectorstore = Chroma(
                embedding_function=self.embeddings, persist_directory=self.persist_directory)
            self.retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 3})
            return

        # NOTE: Hotfixed function in library that does not activate batching
        self.vectorstore = Chroma.from_documents(
            documents=self.split_documents(
                docs, split_strategy=SplitStrategy.SEMANTIC),
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
        )
        self.retriever = self.vectorstore.as_retriever()

    def add_documents_to_vectorstore(self, new_docs: List[Document]):
        logging.debug("Adding documents to vectorstore")
        if self.vectorstore is None:
            raise ValueError(
                "Vectorstore not initialized. Call create_vectorstore() first.")

        self.vectorstore.add_documents(
            documents=self.split_documents(new_docs),
            embedding=self.embeddings,
        )
        self.retriever = self.vectorstore.as_retriever()

    def create_rag_chain(self, chain_type: ChainType = ChainType.STUFF):
        logging.debug("Creating RAG chain")
        system_prompt = """
*Who you are:*
You are a helpful and informative chatbot that answers questions using text from the reference passage included below. 
Respond in a complete sentence and make sure that your response is easy to understand for everyone. 
Maintain a friendly and conversational tone. If the passage is irrelevant, feel free to ignore it.

{summaries}
        """
        logging.debug(system_prompt)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{question}"),
            ]
        )

        if chain_type == ChainType.STUFF:
            self.rag_chain = RetrievalQAWithSourcesChain.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt}
            )
        elif chain_type == ChainType.REFINE:
            self.rag_chain = RetrievalQAWithSourcesChain.from_chain_type(
                llm=self.llm,
                chain_type="refine",
                retriever=self.retriever,
                return_source_documents=True,
            )

    def query(self, input_text):
        if not self.rag_chain:
            raise ValueError(
                "RAG chain not initialized. Call create_rag_chain() first.")

        result = self.rag_chain.invoke({"question": input_text})
        result['cleaned_sources'] = list(set(
            [f"File: {doc.metadata['source']} (p. {doc.metadata['page'] + 1})" for doc in result['source_documents']]))
        result['answer'] = result['answer'].strip()
        return result


def print_result(query, result):
    relevant_sources = '\n'.join(result['cleaned_sources'])

    output_text = f"""\n
### Question:
{query}\n
### Answer:
{result['answer'].strip()}\n
### Sources:
{result['sources']}\n
### All relevant sources:
{relevant_sources}
    """
    return (output_text)


def main():
    rag = RAGSingleton()

    # Load PDF
    docs = rag.load_pdfs_from_directory("data")
    logging.info(f"Number of documents: {len(docs)}")

    # Initialize LLM
    rag.initialize_llm(provider=LLMProvider.GEMINI, project="gen-lang-client-0323803568")

    # Create vectorstore
    rag.create_vectorstore(docs, True)

    # Create RAG chain
    rag.create_rag_chain(chain_type=ChainType.STUFF)

    print("How can kalytera help?")
    while True:
        query = input("")

        results = rag.query(query)
        logging.info(print_result(query, results))
        # print(f"Response: {results}")
    # # Query
    # queries = [
    #     "Who should I contact regarding the import and exports restrictions of cryptographic technology between different countries?",
    #     "Who is the owner of the cryptography management policy?"
    # ]
    # for query in queries:
    #     results = rag.query(query)
    #     logging.info(print_result(query, results))


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    # from utils.logs import get_next_log_filename
    # log_directory = "logs"
    # os.makedirs(log_directory, exist_ok=True)
    # log_file = get_next_log_filename(log_directory, "run")
    # logging.basicConfig(level=logging.DEBUG,
    #                     format="%(asctime)s %(levelname)s %(message)s",
    #                     handlers=[
    #                         logging.FileHandler(log_file),
    #                         logging.StreamHandler()
    #                     ])

    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(message)s")
    main()