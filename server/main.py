from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import io
import json
import os
import traceback
import uuid
from datetime import datetime

app = FastAPI()

# Permitir CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar modelo CLIP
print("⏳ Cargando modelo CLIP...")
model_name = "openai/clip-vit-base-patch32"
processor = CLIPProcessor.from_pretrained(model_name)
model = CLIPModel.from_pretrained(model_name)
model.eval()
print("✅ Modelo CLIP cargado.")

# ✅ PROMPTS MEJORADOS: Descripciones detalladas en vez de solo nombres
POKEMON_PROMPTS = {
    "Pikachu": "Pikachu yellow electric mouse Pokémon with red cheeks and lightning bolt tail",
    "Charizard": "Charizard orange fire dragon Pokémon with wings and flame tail",
    "Bulbasaur": "Bulbasaur green dinosaur Pokémon with plant bulb on back",
    "Squirtle": "Squirtle blue turtle Pokémon with shell and water abilities",
    "Eevee": "Eevee brown fox-like Pokémon with fluffy collar and big ears",
    "Mewtwo": "Mewtwo purple psychic Pokémon with long tail and humanoid shape",
    "Jigglypuff": "Jigglypuff pink round balloon Pokémon with big eyes and marker",
    "Meowth": "Meowth cream colored cat Pokémon with coin on forehead",
    "Psyduck": "Psyduck yellow duck Pokémon holding head with headache",
    "Machamp": "Machamp gray four-armed muscular fighting Pokémon",
    "Gengar": "Gengar purple ghost Pokémon with mischievous grin and spikes",
    "Snorlax": "Snorlax large blue black sleeping Pokémon blocking path",
    "Dragonite": "Dragonite orange dragon Pokémon with wings and friendly face",
    "Lucario": "Lucario blue black jackal Pokémon with aura sensing abilities",
    "Garchomp": "Garchomp blue shark dragon Pokémon with fins and fierce look",
    "Greninja": "Greninja blue frog ninja Pokémon with tongue scarf",
    "Charmander": "Charmander orange lizard Pokémon with flame on tail tip",
    "Charmeleon": "Charmeleon orange evolved lizard Pokémon with claws and flame",
    "Venusaur": "Venusaur green dinosaur Pokémon with large flower on back",
    "Blastoise": "Blastoise blue turtle Pokémon with water cannons on shell",
    "Mew": "Mew pink small cat-like mythical Pokémon with long tail",
    "Rayquaza": "Rayquaza green serpentine dragon Pokémon that lives in ozone layer",
    "Gyarados": "Gyarados blue red sea serpent Pokémon with fierce expression",
    "Lapras": "Lapras blue water transport Pokémon with shell and gentle nature",
    "Articuno": "Articuno blue ice bird legendary Pokémon with long tail feathers",
    "Zapdos": "Zapdos yellow electric bird legendary Pokémon with sharp beak",
    "Moltres": "Moltres orange fire bird legendary Pokémon with flame wings",
}

# Lista simple de nombres
POKEMON_LIST = list(POKEMON_PROMPTS.keys())

# Ruta absoluta para deck.json
DECK_FILE = os.path.join(os.path.dirname(__file__), "deck.json")
if not os.path.exists(DECK_FILE):
    with open(DECK_FILE, "w") as f:
        json.dump([], f)
print(f"📁 Deck file: {DECK_FILE}")

def load_deck():
    try:
        with open(DECK_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_deck(deck):
    with open(DECK_FILE, "w") as f:
        json.dump(deck, f, indent=2)


def save_pokemon(pkmn_data):
    try:
        deck = load_deck()
        deck.append(pkmn_data)
        save_deck(deck)
        print(f"✅ Carta guardada en {DECK_FILE}")
    except Exception as e:
        print(f"❌ Error guardando: {e}")

@app.get("/")
async def root():
    return {"message": "🎮 Pokémon Card Server", "pokemons": len(POKEMON_LIST)}

@app.get("/health")
async def health_check():
    return {"status": "ok", "model": "CLIP", "pokemons": len(POKEMON_LIST)}

@app.post("/upload")
async def upload_drawing(file: UploadFile = File(...)):
    try:
        print(f"📥 Recibiendo: {file.filename}")
        
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        print(f"✅ Imagen: {image.size}")

        # ✅ Usar PROMPTS DESCRIPTIVOS en vez de solo nombres
        texts = [POKEMON_PROMPTS[name] for name in POKEMON_LIST]
        
        inputs = processor(text=texts, images=image, return_tensors="pt", padding=True, truncation=True)
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        logits_per_image = outputs.logits_per_image
        probs = torch.softmax(logits_per_image, dim=1)[0]
        
        # Top 3
        top_values, top_indices = torch.topk(probs, min(3, len(POKEMON_LIST)))
        
        print("📊 Top 3:")
        for i, (idx, val) in enumerate(zip(top_indices, top_values)):
            pkmn_name = POKEMON_LIST[idx.item()]
            print(f"   {i+1}. {pkmn_name}: {val.item()*100:.2f}%")
        
        best_idx = top_indices[0].item()
        pkmn_name = POKEMON_LIST[best_idx]
        similarity = top_values[0].item()
        
        print(f"🏆 Resultado: {pkmn_name} ({similarity*100:.2f}%)")

        # Calcular stats
        if similarity < 0.10:
            hp = 30
            attack = 20
        else:
            hp = int(50 + similarity * 100)
            attack = int(30 + similarity * 70)
        
        hp = max(30, min(150, hp))
        attack = max(20, min(100, attack))

        card = {
            "id": str(uuid.uuid4()),
            "pokemon": pkmn_name,
            "hp": hp,
            "attack": attack,
            "similarity": round(similarity, 4),
            "created_at": datetime.now().isoformat()
        }
        
        save_pokemon(card)
        return JSONResponse(status_code=200, content=card)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/deck")
async def get_deck():
    try:
        print(f"📖 Leyendo deck desde: {DECK_FILE}")
        deck = load_deck()
        print(f"✅ Deck tiene {len(deck)} cartas")
        return {"total_cards": len(deck), "cards": deck}
    except Exception as e:
        print(f"❌ Error leyendo deck: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 