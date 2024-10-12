from langchain_community.document_loaders import PyPDFLoader
from langchain_google_vertexai import ChatVertexAI
from langchain_chroma import Chroma
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
import json

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
        self.embeddings = self.initialize_embeddings()
        self.persist_directory = persist_directory

    def load_json(self, file_path: str) -> List[Document]:
        logging.debug(f"Loading JSON: {file_path}")
        documents = []
        try:
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
                if isinstance(data, list):
                    for index, item in enumerate(data):
                        content = json.dumps(item, indent=2)
                        doc = Document(
                            page_content=content,
                            metadata={
                                "source": file_path,
                                "index": index
                            }
                        )
                        documents.append(doc)
                elif isinstance(data, dict):
                    content = json.dumps(data, indent=2)
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": file_path
                        }
                    )
                    documents.append(doc)
        except Exception as e:
            logging.error(f"Error loading JSON {file_path}: {str(e)}")
        return documents
    
    def load_jsons_from_directory(self, directory_path: str) -> List[Document]:
        logging.debug(f"Attempting to load JSONs from directory: {directory_path}")
        logging.debug(f"Current working directory: {os.getcwd()}")
        
        if not os.path.exists(directory_path):
            logging.error(f"Directory does not exist: {directory_path}")
            raise FileNotFoundError(f"Directory does not exist: {directory_path}")
        
        all_documents = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".json"):
                file_path = os.path.join(directory_path, filename)
                documents = self.load_json(file_path)
                all_documents.extend(documents)
        
        logging.debug(f"Loaded {len(all_documents)} documents from {directory_path}")
        return all_documents

    def initialize_llm(self, model="gemini-1.5-flash", temperature=0, project="gen-lang-client-0323803568"):
        logging.debug("Initializing LLM")
        self.llm = ChatVertexAI(
            model=model,
            temperature=temperature,
            project=project
        )

    def initialize_embeddings(self, hf_token=None, model_name="sentence-transformers/all-MiniLM-l6-v2"):
        logging.debug("Initializing embeddings")

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
                self.embeddings, breakpoint_threshold_type="percentile"
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
**Who you are:**
You are a helpful and informative chatbot that answers questions using text from the reference passage included below. 
Your job is to help people to upskills themselves by giving them suggestion so that they can be a more competitive candidate in job application.
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

    def query(self, cur_job, new_job, skill):
        input_text = f"""
I am a {cur_job} and I wish to change my job to {new_job}. My existing skills are {skill}. What do I have to do or learn 
to accomplish my goal? Suggest me sources for me to learn the required additional skills.
"""
        if not self.rag_chain:
            raise ValueError(
                "RAG chain not initialized. Call create_rag_chain() first.")

        result = self.rag_chain.invoke({"question": input_text})
        result['cleaned_sources'] = list(set(
            [f"File: {doc.metadata['source']}" for doc in result['source_documents']]))
        result['answer'] = result['answer'].strip()
        return result


def print_result(cur_job, new_job, skill, result):
    relevant_sources = '\n'.join(result['cleaned_sources'])

    output_text = f"""\n
### What is your current job?
{cur_job}\n
### What is your desired new job?
{new_job}\n
### What skills do you have?
{skill}\n
### Answer:
{result['answer'].strip()}\n
### Sources:
{result['sources']}\n
### All relevant sources:
{relevant_sources}
    """
    return (output_text)


def ai(cur_job, new_job, skill):
    rag = RAGSingleton()

    # Load PDF
    docs = rag.load_jsons_from_directory("data")
    logging.info(f"Number of documents: {len(docs)}")

    # Initialize LLM
    rag.initialize_llm()

    # Create vectorstore
    rag.create_vectorstore(docs, True)

    # Create RAG chain
    rag.create_rag_chain(chain_type=ChainType.STUFF)

    # # Query
    # print("Please answer the following question\n")
    # cur_job = input("What is your current job? ")
    # new_job = input("What is your desired new job? ")
    # skill = input("What skills do you have? ")

    # for query in queries:
    results = rag.query(cur_job, new_job, skill)
    return results['answer'].strip()
    # logging.info(print_result(cur_job, new_job, skill, results))


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

    ai()