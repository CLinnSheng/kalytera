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
from dotenv import load_dotenv
import logging
import os
import csv
import json
import traceback
import sys


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
        logging.debug(f"Loading JSONs from directory: {directory_path}")
        all_documents = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".json"):
                file_path = os.path.join(directory_path, filename)
                documents = self.load_json(file_path)
                all_documents.extend(documents)
        return all_documents
    
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

    def query(self, cur_work, new_work, skills):
            input_text = f"""
I am a {cur_work} and I wish to be a {new_work}. The skillsets that I have are {skills}. What else should I learn to 
accomplish my goal? On top of that, suggest me resources for me to learn the required additional skills.
"""

            if not self.rag_chain:
                raise ValueError(
                    "RAG chain not initialized. Call create_rag_chain() first.")

            result = self.rag_chain.invoke({"question": input_text})
            result['cleaned_sources'] = list(set(
                [self.format_source_info(doc) for doc in result['source_documents']]))
            result['answer'] = result['answer'].strip()
            return result
    
    def format_source_info(self, doc):
        source = doc.metadata.get('source', 'Unknown source')
        if 'page' in doc.metadata:
            return f"File: {source} (p. {doc.metadata['page'] + 1})"
        elif 'row' in doc.metadata:
            return f"File: {source} (row {doc.metadata['row'] + 1})"
        else:
            return f"File: {source}"

def print_result(cur_work, new_work, skills, result):
    relevant_sources = '\n'.join(result['cleaned_sources'])

    output_text = f"""\n
### What is your current occupation?
{cur_work}\n
### What job do you wish to transition into?
{new_work}\n
### What skills do you have?
{skills}\n
### Answer:
{result['answer'].strip()}\n
### Sources:
{result['sources']}\n
### All relevant sources:
{relevant_sources}
    """
    return (output_text)

def get_user_input():
    print("Please answer the following questions:")
    cur_work = input("What is your current occupation? ")
    new_work = input("What job do you wish to transition into? ")
    skills = input("What skills do you have? ")
    return cur_work, new_work, skills


# def main():
#     rag = RAGSingleton()

#     # Load PDF
#     docs = rag.load_jsons_from_directory("data")
#     logging.info(f"Number of documents: {len(docs)}")

#     # Initialize LLM
#     rag.initialize_llm(provider=LLMProvider.GEMINI, project="gen-lang-client-0323803568")

#     # Create vectorstore
#     rag.create_vectorstore(docs, True)

#     # Create RAG chain
#     rag.create_rag_chain(chain_type=ChainType.STUFF)

#     while True:
#         cur_work, new_work, skills = get_user_input()
        
#         results = rag.query(cur_work, new_work, skills)
#         logging.info(print_result(cur_work, new_work, skills, results))

#         new_query = input("Do you have other queries? (y/n): ").lower()
#         if new_query != 'y':
#             break

def main():
    logging.info("Entering main function")
    try:
        rag = RAGSingleton()
        logging.info("RAGSingleton initialized")

        # Load JSON
        logging.info("Loading JSON documents")
        try:
            docs = rag.load_jsons_from_directory("data")
            logging.info(f"Number of documents: {len(docs)}")
        except Exception as e:
            logging.error(f"Error loading JSON documents: {str(e)}")
            logging.debug(traceback.format_exc())
            return

        # Initialize LLM
        logging.info("Initializing LLM")
        try:
            rag.initialize_llm(provider=LLMProvider.GEMINI, project="gen-lang-client-0323803568")
            logging.info("LLM initialized")
        except Exception as e:
            logging.error(f"Error initializing LLM: {str(e)}")
            logging.debug(traceback.format_exc())
            return

        # Create vectorstore
        logging.info("Creating vectorstore")
        try:
            rag.create_vectorstore(docs, True)
            logging.info("Vectorstore created")
        except Exception as e:
            logging.error(f"Error creating vectorstore: {str(e)}")
            logging.debug(traceback.format_exc())
            return

        # Create RAG chain
        logging.info("Creating RAG chain")
        try:
            rag.create_rag_chain(chain_type=ChainType.STUFF)
            logging.info("RAG chain created")
        except Exception as e:
            logging.error(f"Error creating RAG chain: {str(e)}")
            logging.debug(traceback.format_exc())
            return

        logging.info("Entering main loop")
        while True:
            try:
                cur_work, new_work, skills = get_user_input()
                results = rag.query(cur_work, new_work, skills)
                logging.info(print_result(cur_work, new_work, skills, results))

                new_query = input("Do you have other queries? (y/n): ").lower()
                if new_query != 'y':
                    break
            except Exception as e:
                logging.error(f"Error in main loop: {str(e)}")
                logging.debug(traceback.format_exc())
                break

    except Exception as e:
        logging.error(f"Unexpected error in main function: {str(e)}")
        logging.debug(traceback.format_exc())

    logging.info("Exiting main function")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(message)s")
    print("Entering main function...")
    main()
