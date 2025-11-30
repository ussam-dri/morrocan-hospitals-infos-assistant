import os
import re
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


#AIzaSyDjYTZ0s-T7AL1xT3Os4lcxuhgHaqX9IBE
#AIzaSyBGEQPAdcFZ9i4-fQKWSTTbjEPf13F7bCA
#--diff
#AIzaSyDH-F93LIMeI5ExoQnw51gYfV222bOhRdY
#AIzaSyCrssBJPrXPiyqxvNTatQ1TaGvQBrd5tJ4
# Configure Gemini

genai.configure(api_key="AIzaSyCrssBJPrXPiyqxvNTatQ1TaGvQBrd5tJ4")
model = genai.GenerativeModel("models/gemini-2.0-flash") # Updated to flash for speed, or use pro

# Initialize FastAPI
app = FastAPI(title="Hospital Chatbot API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Vector DB Global Variable
vector_store = None

@app.on_event("startup")
async def startup_event():
    global vector_store
    print("Loading Vector Database...")
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_store = Chroma(
            collection_name="hopitaux_collection",
            persist_directory="./chromadb_data",
            embedding_function=embeddings
        )
        try:
            count = vector_store._collection.count()
            print(f"✅ Database Loaded. Found {count} documents in collection.")
        except Exception:
            print("⚠️  Database Loaded but collection may be empty. Run ingest.py first.")
    except Exception as e:
        print(f"❌ Error loading database: {e}")
        vector_store = None

# Define Request Model
class ChatRequest(BaseModel):
    message: str 
    language: str = "fr"

# Define Response Model
class ChatResponse(BaseModel):
    response: str
    message: str = "" 
    sources: list[dict] = []

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not vector_store:
        raise HTTPException(status_code=500, detail="Database not loaded. Please check server logs.")

    try:
        user_language = request.language.lower()
        if user_language not in ["fr", "ar", "en"]:
            user_language = "fr"
        
        user_query = request.message
        
        # --- Step 1: Translate Query to French (if needed) ---
        if user_language != "fr":
            translation_prompt = f"""
            Translate the following text to French. Only return the translation, nothing else.
            Text: {user_query}
            """
            try:
                translation_response = model.generate_content(translation_prompt)
                search_query = translation_response.text.strip()
            except Exception as e:
                print(f"Translation error: {e}")
                search_query = user_query
        else:
            search_query = user_query
        
        # --- Step 2: Search Vector DB ---
        try:
            docs = vector_store.similarity_search(search_query, k=5)
        except Exception:
             return ChatResponse(
                response="Erreur de base de données.",
                message="Erreur de base de données."
            )
        
        if not docs:
            no_results_messages = {
                "fr": "Aucune information trouvée.",
                "ar": "لا توجد معلومات.",
                "en": "No info found."
            }
            msg = no_results_messages.get(user_language, "Aucune information trouvée.")
            return ChatResponse(response=msg, message=msg, sources=[])
        
        context_text = "\n\n".join([d.page_content for d in docs])

        # --- Step 3: Generate Answer (STRICT NO MARKDOWN) ---
        french_prompt = f"""Tu es un assistant médical utile. Tu as accès à une base de données d'hôpitaux et de cliniques au Maroc.

Utilise le contexte suivant pour répondre à la question de l'utilisateur.

RÈGLES DE FORMATAGE ABSOLUMENT OBLIGATOIRES - VIOLATION = ERREUR :
- INTERDIT : Markdown (**, *, ##, __, _, etc.)
- INTERDIT : Astérisques pour le formatage
- OBLIGATOIRE : Texte brut uniquement
- Pour les listes : utilise des tirets simples (-)
- Format recommandé : "Nom : Détail" ou "Nom - Détail"

Contexte:
{context_text}

Question: {search_query}

Réponds en texte brut simple, SANS AUCUN formatage markdown, SANS astérisques :
"""
        
        french_response = model.generate_content(french_prompt)
        raw_answer = french_response.text or "Pas de réponse générée."
        
        # Clean markdown from response (remove **, *, ##, etc.)
        import re
        french_answer = re.sub(r'\*\*([^*]+)\*\*', r'\1', raw_answer)  # Remove **bold**
        french_answer = re.sub(r'\*([^*]+)\*', r'\1', french_answer)   # Remove *italic*
        french_answer = re.sub(r'#{1,6}\s+', '', french_answer)          # Remove headers
        french_answer = re.sub(r'__([^_]+)__', r'\1', french_answer)   # Remove __bold__
        french_answer = re.sub(r'_([^_]+)_', r'\1', french_answer)     # Remove _italic_
        french_answer = re.sub(r'\*\s+', '- ', french_answer)           # Convert * lists to -
        french_answer = re.sub(r'^\s*[-*]\s+', '- ', french_answer, flags=re.MULTILINE)  # Normalize lists
        
        # --- Step 4: Translate Answer (if needed) ---
        if user_language == "fr":
            final_answer = french_answer
        else:
            target_lang_name = {"ar": "Arabic", "en": "English"}.get(user_language, "French")
            translation_prompt = f"""
            Translate this text to {target_lang_name}. 
            CRITICAL: Do not add any Markdown formatting (no **, no ##). Keep it plain text.
            
            Text:
            {french_answer}
            """
            try:
                translation_response = model.generate_content(translation_prompt)
                raw_translation = translation_response.text.strip()
                # Clean markdown from translated response
                raw_translation = re.sub(r'\*\*([^*]+)\*\*', r'\1', raw_translation)
                raw_translation = re.sub(r'\*([^*]+)\*', r'\1', raw_translation)
                raw_translation = re.sub(r'#{1,6}\s+', '', raw_translation)
                raw_translation = re.sub(r'__([^_]+)__', r'\1', raw_translation)
                raw_translation = re.sub(r'_([^_]+)_', r'\1', raw_translation)
                final_answer = raw_translation
            except Exception:
                final_answer = french_answer

        # --- Step 5: Final Code Cleanup (The Safety Net) ---
        # Explicitly remove any remaining markdown characters
        final_answer = final_answer.replace("**", "").replace("##", "").replace("__", "").replace("*", "")
        # Remove extra blank lines (optional visual cleanup)
        final_answer = re.sub(r'\n\s*\n+', '\n\n', final_answer).strip()

        # Format sources
        formatted_sources = [
            {"title": f"Source {i+1}", "url": "#"} 
            for i, doc in enumerate(docs)
        ]
        
        return ChatResponse(
            response=final_answer,
            message=final_answer,
            sources=formatted_sources
        )

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"status": "running"}

if __name__ == "__main__":
    import uvicorn
    print("Starting Hospital Chatbot API server...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)