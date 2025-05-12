from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import ollama
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # autoriser le frontend à faire des appels à l'API
    allow_credentials=True, # cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel): # envoyer un Json qui contient une seule clé: prompt
    prompt: str

@app.post("/generate")
def generate_text(request: PromptRequest):
    input_prompt = request.prompt

    # Prompt système comme contexte de rôle
    system_prompt = (
    "You are a professional football scout and analyst with expertise in player performance, team tactics, match analysis, "
    "and talent identification. Your task is to respond in a structured, detailed, and expert-level manner strictly related "
    "to football (soccer)."

    "\n\nIf the question is about a **specific player** (e.g., 'Who is Cristiano Ronaldo?'), provide a scouting report with the following sections:\n"
    "- **Player Profile**: Full name, nationality, position(s), height, and career overview.\n"
    "- **Strengths**: Highlight key attributes (e.g., goal scoring, technical skills, versatility, physical fitness).\n"
    "- **Weaknesses**: Discuss any limitations (e.g., defensive work rate, injury history, age).\n"
    "- **Scouts' Remarks**: Insights on playstyle, mentality, and overall impact.\n"
    "- **Conclusion**: Summary of career, contributions, and legacy.\n"

    "\nIf the question is about **team tactics**, describe:\n"
    "- Tactical system used (e.g., 4-3-3 high press).\n"
    "- Role of key players in the system.\n"
    "- Strengths and vulnerabilities of the approach.\n"
    "- Tactical evolution or adaptability over time.\n"

    "\nIf the question concerns a **match analysis**, cover:\n"
    "- Line-ups and formations.\n"
    "- Key moments and turning points.\n"
    "- Tactical decisions made by each manager.\n"
    "- Player performances and standout contributors.\n"

    "\nIf it's about a **transfer or scouting decision**, include:\n"
    "- Player potential and fit within the team.\n"
    "- Financial aspects if relevant.\n"
    "- Long-term implications for both club and player.\n"

    "\nAlways remain accurate, concise, and focused strictly on football. Avoid generic responses or information outside the football context."
    )


    football_keywords = [
        # English
        "football", "soccer", "player", "goal", "match", "transfermarkt",
        "scout", "club", "coach", "striker", "forward", "midfielder", "defender",
        "goalkeeper", "keeper", "team", "formation", "tactics", "league",
        "champions", "cup", "penalty", "assist", "dribble", "offside", "referee",
        "VAR", "injury", "substitute", "fixture", "lineup", "pressing", "possession",

        # French
        "foot", "joueur", "but", "match", "entraîneur", "gardien", "défenseur",
        "milieu", "attaquant", "équipe", "formation", "tactique", "ligue",
        "arbitre", "remplaçant", "blessure", "coup franc", "pénalty", "passe décisive",

        # Spanish
        "fútbol", "jugador", "gol", "partido", "entrenador", "portero", "defensa",
        "centrocampista", "delantero", "equipo", "formación", "táctica", "liga",
        "árbitro", "penalti", "asistencia", "sustituto", "posesión",

        # Italian
        "calcio", "giocatore", "gol", "partita", "allenatore", "portiere",
        "difensore", "centrocampista", "attaccante", "squadra", "formazione",
        "tattica", "campionato", "arbitro", "rigore", "assist", "infortunio",

        # German
        "fußball", "spieler", "tor", "spiel", "trainer", "torwart", "verteidiger",
        "mittelfeldspieler", "stürmer", "mannschaft", "aufstellung", "taktik",
        "liga", "schiedsrichter", "elfmeter", "vorlage", "verletzung"
    ]


    if not any(word.lower() in input_prompt.lower() for word in football_keywords):
        return {"response": "I'm sorry, I can only answer football-related questions."}

    try:
        response = ollama.chat(
            model="llama3.2:3b",  
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_prompt}
            ]
        )
        return {"response": response["message"]["content"]}
    except Exception as e:
        return {"response": f"Ollama API error: {str(e)}"}
