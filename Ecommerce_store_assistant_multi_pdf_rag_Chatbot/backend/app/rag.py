import os
import asyncio
from typing import Dict, Any, List
from app.config import config
from app.pdf_processor import PDFProcessor

# LangChain Imports
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class RAGSystem:
    def __init__(self):
        # Initialize Google GenAI
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            google_api_key=config.GOOGLE_API_KEY
        )

        # Initialize the Chat Model (non-streaming for simpler HTTP requests)
        self.llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL,
            google_api_key=config.GOOGLE_API_KEY,
            temperature=0.3
        )

        self.vector_store = None
        self._setup_chroma_db()

    def _setup_chroma_db(self):
        """Initializes or loads the Chroma vector database from PDF documents."""
        os.makedirs(config.PERSIST_DIR, exist_ok=True)
        chroma_db_path = os.path.join(config.PERSIST_DIR, "chroma.sqlite3")

        if os.path.exists(chroma_db_path):
            print("Loading existing Chroma DB...")
            self.vector_store = Chroma(
                persist_directory=config.PERSIST_DIR,
                embedding_function=self.embeddings
            )
            print("Loaded Chroma DB")
        else:
            print("Creating new Chroma DB from PDFs...")
            pdf_processor = PDFProcessor()
            pdf_chunks = pdf_processor.process_all_pdfs()
            
            if not pdf_chunks:
                print("No documents found to index!")
                return

            texts = [chunk['text'] for chunk in pdf_chunks]
            metadatas = [chunk['metadata'] for chunk in pdf_chunks]

            self.vector_store = Chroma.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas,
                persist_directory=config.PERSIST_DIR
            )
            print("Chroma DB created and persisted")

    async def get_answer_async(self, question: str) -> Dict[str, Any]:
        """
        Retrieves context and generates a full answer.
        Returns a dictionary with content and sources.
        """
        try:
            # 1. Retrieval
            docs = await asyncio.to_thread(
                self.vector_store.similarity_search,
                question, k=config.TOP_K_RESULTS
            )

            if not docs:
                return {
                    "content": "I don't have that information. Try asking about products, returns, or shipping.",
                    "sources": []
                }

            # 2. Prepare sources and context
            sources = list(set([doc.metadata.get('source', 'Document') for doc in docs]))
            context = "\n\n".join([doc.page_content for doc in docs])

            # 3. Build the Chain
            prompt = ChatPromptTemplate.from_template("""
            You are a fast e-commerce assistant for TechStore Pro.
            Answer based ONLY on this context:
            {context}
            
            Question: {question}
            
            Rules:
            - Answer directly (1-2 sentences max if possible)
            - Use bullet points only if really needed
            - If info missing, say "I don't know"
            
            Answer:""")
            
            chain = prompt | self.llm | StrOutputParser()

            # 4. Invoke the chain and wait for full response
            response = await chain.ainvoke({"context": context, "question": question})

            return {
                "content": response,
                "sources": sources
            }

        except Exception as e:
            print(f"RAG Error: {e}")
            return {
                "content": f"Sorry, I encountered an error: {str(e)}",
                "sources": []
            }
