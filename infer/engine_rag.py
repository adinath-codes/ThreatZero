import hashlib
from  pathlib import Path
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from knowledge_loader import ThreatIntelLoader
CURR_DIR = Path(__file__).parent
LOG_FILE = Path(__file__).parent.parent.resolve() / "logs" / "incidents.jsonl"
class EngineRAG:
    def __init__(self):
        self.persistent_dir = CURR_DIR / "chroma_db"
        print("[-] 🧠 Loading Embedding Model (all-MiniLM-L6-v2)...")
        self.embedding_func = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_db = None
        self.intel_loader = ThreatIntelLoader()
        if Path(self.persistent_dir).exists():
            print("[-] 📂 Found existing Vector DB. Loading...")
            self.vector_db = Chroma(
                persist_directory=str(self.persistent_dir),
                embedding_function=self.embedding_func
            )
        else:
            print("[-] ⚠️ No DB found. Starting fresh ingestion...")
            self.refresh_knowledge()
    def refresh_knowledge(self):
        """Downloads data and rebuilds the vector database."""
        print("[-] 🔄 Updating RAG Knowledge Base (This may take a minute)...")
        self.intel_loader.load_mitre_attack()
        self.intel_loader.load_capec()
        self.intel_loader.load_apt_notes()
        raw_docs = self.intel_loader.get_documents()
        if not raw_docs:
            print("❌ No documents to ingest.")
            return
        # 2. Split Text (Chunks)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        splits = text_splitter.split_documents(raw_docs)
        # 3. Store in Vector DB
        print(f"[-] 💾 Saving {len(splits)} chunks to ChromaDB...")
        self.vector_db = Chroma.from_documents(
            documents=splits, 
            embedding=self.embedding_func, 
            persist_directory=str(self.persistent_dir)
        )
        print("[-] ✅ RAG Knowledge Base Ready.")
    def sync_logs_only(self):
        """Only updates logs (Faster than full refresh)"""
        print("[-] 📥 Syncing latest logs to RAG...")
        log_docs = self._process_logs()
        
        if log_docs:
            self.vector_db.add_documents(log_docs)
            print(f"[-] ✅ Added {len(log_docs)} recent log entries to Brain.")
        else:
            print("[-] 🤷 No logs found.")
    def _process_logs(self):
        """Reads JSONL logs and converts them to AI-readable text"""
        if not Path(LOG_FILE).exists():
            return []

        docs = []
        with open(LOG_FILE, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    
                    # Convert JSON to a "Story" the AI understands
                    # We create a unique ID hash to avoid duplicate log entries in DB
                    log_id = hashlib.md5(line.encode()).hexdigest()
                    
                    content = (
                        f"REAL-TIME LOG ENTRY:\n"
                        f"Time: {entry.get('date')}\n"
                        f"Attacker IP: {entry.get('attacker_ip')}\n"
                        f"Attack Type: {entry.get('verdict')}\n"
                        f"Payload/Command: {entry.get('payload') or entry.get('input_cmd')}\n"
                        f"Action Taken: {entry.get('action_taken')}\n"
                        f"Source: {entry.get('source')}\n"
                    )
                    from langchain_core.documents import Document
                    
                    docs.append(Document(
                        page_content=content,
                        metadata={"source": "realtime_logs", "log_id": log_id, "ip": entry.get('attacker_ip')}
                    ))
                except json.JSONDecodeError:
                    continue
        return docs
    def query(self,query_txt,k=5):
        """Queries the vector database and returns top-k similar documents."""
        if not self.vector_db:
            print("❌ Vector DB not initialized.")
            return []
        results = self.vector_db.similarity_search(query_txt, k=k)
        context_text = "\n\n".join([doc.page_content for doc in results])
        return context_text

# Test block
# if __name__ == "__main__":
#     rag = EngineRAG()
#     # rag.refresh_knowledge() # Uncomment to force update
#     print(rag.query("How do I fix SQL Injection?"))