import os
import requests
import json


class ThreatIntelLoader:
    def __init__(self):
        self.knowledge_docs = []

    # --- 1. MITRE ATT&CK (STIX Data) ---
    def load_mitre_attack(self):
        print("[-] 📥 Downloading MITRE ATT&CK Data...")
        url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print("❌ Failed to download MITRE data.")
                return

            data = response.json()
            objects = data.get("objects", [])
            
            print(f"[-] Parsing {len(objects)} MITRE objects...")
            
            for obj in objects:
                # We only want Techniques (attack-pattern)
                if obj.get("type") == "attack-pattern":
                    name = obj.get("name", "Unknown")
                    description = obj.get("description", "No description.")
                    ext_id = "Unknown"
                    
                    # Extract ID (e.g., T1059)
                    for ref in obj.get("external_references", []):
                        if ref.get("source_name") == "mitre-attack":
                            ext_id = ref.get("external_id")
                    
                    # Create readable text for the AI
                    text_content = (
                        f"SOURCE: MITRE ATT&CK\n"
                        f"TECHNIQUE_ID: {ext_id}\n"
                        f"NAME: {name}\n"
                        f"DESCRIPTION: {description}\n"
                    )
                    from langchain_core.documents import Document
                    self.knowledge_docs.append(
                        Document(page_content=text_content, metadata={"source": "mitre_attack", "id": ext_id})
                    )
            print(f"[-] ✅ MITRE ATT&CK Loaded ({len(self.knowledge_docs)} docs).")
            
        except Exception as e:
            print(f"❌ Error loading MITRE: {e}")

    # --- 2. CAPEC (Common Attack Pattern) ---
    def load_capec(self):
        print("[-] 📥 Downloading CAPEC Data...")
        # Using a simplified URL or logic for CAPEC
        url = "https://capec.mitre.org/data/definitions/3000.json" 
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print("❌ Failed to download CAPEC data.")
                return

            data = response.json()
            objects = data.get("objects", [])
            
            for obj in objects:
                if obj.get("type") == "attack-pattern":
                    name = obj.get("name")
                    description = obj.get("description", "")
                    
                    text_content = (
                        f"SOURCE: CAPEC Attack Pattern\n"
                        f"NAME: {name}\n"
                        f"DESCRIPTION: {description}\n"
                    )
                    from langchain_core.documents import Document
                    self.knowledge_docs.append(
                        Document(page_content=text_content, metadata={"source": "capec"})
                    )
            print("[-] ✅ CAPEC Loaded.")

        except Exception as e:
            print(f"❌ Error loading CAPEC: {e}")

    # --- 3. APTNotes (PDF Reports) ---
    def load_apt_notes(self, folder_path="intelligence/knowledge_base/apt_reports"):
        """
        Expects PDF files in 'intelligence/knowledge_base/apt_reports'
        """
        if not os.path.exists(folder_path):
            print(f"[-] ⚠️ APTNotes folder not found at {folder_path}. Creating it...")
            os.makedirs(folder_path, exist_ok=True)
            return

        print(f"[-] 📄 Parsing APTNotes PDFs from {folder_path}...")
        try:
            from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
            loader = DirectoryLoader(folder_path, glob="*.pdf", loader_cls=PyPDFLoader)
            docs = loader.load()
            
            if not docs:
                print("[-] ⚠️ No PDFs found. Skipping.")
                return

            # Tag them so the AI knows these are case studies
            for doc in docs:
                doc.page_content = "SOURCE: REAL WORLD CASE STUDY (APTNotes)\n" + doc.page_content
                doc.metadata["source"] = "apt_notes"
                
            self.knowledge_docs.extend(docs)
            print(f"[-] ✅ Loaded {len(docs)} PDF pages from APTNotes.")
        except Exception as e:
            print(f"❌ Error loading PDFs: {e}")

    def get_documents(self):
        return self.knowledge_docs