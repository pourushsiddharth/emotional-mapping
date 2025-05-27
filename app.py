import os
import json
import re
import html
from flask import Flask, request, render_template
from graphviz import Digraph
import google.generativeai as genai
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logging.critical("CRITICAL: GEMINI_API_KEY not found in environment variables. Application will likely fail.")
genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemma-3-27b-it" 


try:
    model = genai.GenerativeModel(model_name=MODEL_NAME)
    logging.info(f"Initialized GenerativeModel with '{MODEL_NAME}'")
except Exception as e:
    logging.error(f"Failed to initialize GenerativeModel '{MODEL_NAME}': {e}")
    model = None

app = Flask(__name__)
MAX_SITUATION_LENGTH = 240

def build_prompt(data):
    situation = html.escape(data.get("situation", "")[:MAX_SITUATION_LENGTH])
    language = html.escape(data.get("preferred_language", "English"))
    age = html.escape(data.get("age", "unknown"))
    location = html.escape(data.get("country", "unknown"))

    prompt = f"""
You are an expert Emotional Mapping AI. Your goal is to create a VERY CONCISE emotional map BASED ON {situation}, {age}, {location} and with FEW key stages (3-4 ideally).

THE OUTPUT MUST BE A SINGLE, VALID JSON OBJECT, AND NOTHING ELSE.

Your analysis must identify:
1. Core emotions in {language} (lists).
2. Emotional transitions in {language} (all).
3. Trigger analysis in {language} (all).
4. Psychological interpretation in {language} (SEPERATED BY COMMAS AND NOTHING ELSE, NO BRACKETS, lists).
5. A visual map (emotional_stages and connections for Graphviz).
   - 'emotional_stages': FEW (3-4) distinct emotional states with 'stage' (ID and VERY SHORT label/emoji, 1-2 words max) and a 'description' (for tooltips, keep it short and informative, ~5-10 words).
   - 'connections': Link stages using 'source' and 'target'. Optional 'label' (1 word), DO NOT INCLUDE NUMBERS in the labels.
6. Suggestions for healing in {language} (practical and scientifically proven, lists).
7. A final empathetic message in the specified language (very short, in {language}).

User input:
{{
  "situation": "{situation}",
  "preferred_language": "{language}",
  "age": "{age}",
  "location": "{location}"
}}

Output JSON:
{{
  "emotional_map": {{
    "core_emotions": ["Stress", "Focus"],
    "emotional_transitions": ["Stress to focus."],
    "trigger_analysis": "Deadline.",
    "psychological_interpretation": "Adapting to pressure.",
    "emotional_stages": [
      {{ "stage": "Pressure 😟", "description": "Initial task awareness." }},
      {{ "stage": "Plan 🤔", "description": "Strategizing approach." }},
      {{ "stage": "Action 💪", "description": "Beginning the work." }}
    ],
    "connections": [
      {{ "source": "Pressure 😟", "target": "Plan 🤔" }},
      {{ "source": "Plan 🤔", "target": "Action 💪", "label": "Start" }}
    ]
  }},
  "healing_suggestions": [ "Short breaks.", "Prioritize." ],
  "final_message": "You can do this! 👍"
}}
"""
    return prompt

def extract_json_from_text(text):
    match = re.search(r"```(?:json)?\s*(\{.*\})\s*```|(\{.*\})", text, re.DOTALL | re.MULTILINE)
    if match:
        json_str = match.group(1) or match.group(2)
        if json_str:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decoding failed: {e}. Input text (partial): {json_str[:200]}")
                return None
    logging.warning("No JSON block found in AI response.")
    return None

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", previous_input={})

@app.route("/map-emotions", methods=["POST"])
def map_emotions():
    if not model:
        logging.error("Generative model not initialized. Cannot map emotions.")
        return render_template("index.html", error="⚠️ AI Model is not available. Please contact support.", previous_input=request.form)

    user_data_form = request.form
    situation = user_data_form.get("situation", "").strip()

    if not situation:
        return render_template("index.html", error="⚠️ Please describe your situation.", previous_input=user_data_form)
    if len(situation) > MAX_SITUATION_LENGTH:
        return render_template("index.html", error=f"⚠️ Explanation must be under {MAX_SITUATION_LENGTH} characters.", previous_input=user_data_form)

    data_for_prompt = {
        "situation": situation,
        "preferred_language": user_data_form.get("preferred_language", "English"),
        "age": user_data_form.get("age", "unknown"),
        "country": user_data_form.get("country", "unknown")
    }

    prompt_text = build_prompt(data_for_prompt)
    logging.info(f"Processing request for situation: {data_for_prompt.get('situation')[:70]}...")

    response_data = {
        "flowchart_svg": None, "core_emotions": [], "emotional_transitions": [],
        "trigger_analysis": "", "psychological_interpretation": "", "healing_suggestions": [],
        "final_message": "Analysis could not be completed.", "raw_output": "",
        "previous_input": data_for_prompt,
    }

    try:
        generation_config = genai.types.GenerationConfig(candidate_count=1, temperature=0.5)
        ai_response = model.generate_content(prompt_text, generation_config=generation_config)
        raw_ai_text = ai_response.text
        response_data["raw_output"] = raw_ai_text
        logging.info("Received AI response.")

        parsed_json = extract_json_from_text(raw_ai_text)

        if parsed_json:
            emotional_map_data = parsed_json.get("emotional_map", {})
            response_data.update({
                "core_emotions": emotional_map_data.get("core_emotions", []),
                "emotional_transitions": emotional_map_data.get("emotional_transitions", []),
                "trigger_analysis": emotional_map_data.get("trigger_analysis", ""),
                "psychological_interpretation": emotional_map_data.get("psychological_interpretation", ""),
                "healing_suggestions": parsed_json.get("healing_suggestions", []),
                "final_message": parsed_json.get("final_message", "Analysis processed, final message missing.")
            })

            stages = emotional_map_data.get("emotional_stages", [])
            connections = emotional_map_data.get("connections", [])

            if stages:
                dot = Digraph(format='svg', graph_attr={'concentrate': 'true'})
                dot.attr(rankdir='LR', 
                         bgcolor='white', 
                         newrank='true', 
                         splines='spline', 
                         pad="0.2",        
                         nodesep="0.4",    
                         ranksep="0.5",    
                         dpi="72"          
                        )
                
                default_node_fillcolor = '#ffffff' 
                default_node_fontcolor = '#212121' 
                default_node_bordercolor = '#BDBDBD' 
                edge_color = '#B0BEC5' 

                dot.attr('node', 
                         shape='box', 
                         style='filled,rounded', 
                         fillcolor=default_node_fillcolor, 
                         fontsize='8', 
                         fontcolor=default_node_fontcolor, 
                         penwidth='1',  
                         color=default_node_bordercolor, 
                         margin="0.1,0.08", 
                         fixedsize='true', 
                         height="0.5",     
                         width="1.0")      

                dot.attr('edge', 
                         color=edge_color, 
                         arrowhead='empty', 
                         arrowsize='0.5', 
                         penwidth='0.8',  
                         fontsize='6',    
                         fontcolor='#616161',
                         minlen="1") 


                for i, stage_data in enumerate(stages):
                    node_id_raw = stage_data.get("stage","").strip()
                    description_raw = stage_data.get("description","").strip() 
                    
                    if node_id_raw:
                        label_display = node_id_raw
                        
                        max_chars_per_line = 12 
                        if len(label_display) > max_chars_per_line : 
                            wrapped_label_lines = []
                            current_line = ""
                            for word in label_display.split():
                                if not current_line: current_line = word
                                elif len(current_line) + 1 + len(word) <= max_chars_per_line: current_line += " " + word
                                else:
                                    wrapped_label_lines.append(current_line)
                                    current_line = word
                            if current_line: wrapped_label_lines.append(current_line)
                            label_display = r"\n".join(wrapped_label_lines[:2]) 
                            if len(wrapped_label_lines) > 2: label_display += r"..."


                        node_specific_attrs = {}
                        if description_raw:
                            tooltip_text = description_raw.replace('"', '\\"')
                            node_specific_attrs['tooltip'] = tooltip_text
                        
                        dot.node(node_id_raw, label=label_display, **node_specific_attrs)

                for conn_data in connections:
                    source = conn_data.get("source","").strip()
                    target = conn_data.get("target","").strip()
                    edge_label = conn_data.get("label","").strip()
                    if source and target: 
                        dot.edge(source, target, label=edge_label)
                
                if dot.body:
                    response_data["flowchart_svg"] = dot.pipe().decode("utf-8")
                    logging.info("Graphviz SVG generated (LR, attempting compact).")
                else:
                    logging.warning("Graphviz: No stages/connections to draw from AI response.")
            else:
                logging.warning("No 'emotional_stages' in AI response for graph generation.")
        else:
            response_data["final_message"] = "⚠️ AI response could not be parsed. Please try rephrasing."
            logging.error(f"Failed to parse JSON from AI. Raw text (partial): {raw_ai_text[:200]}")

    except genai.types.generation_types.BlockedPromptException as bpe:
        logging.warning(f"AI generation blocked by safety settings: {bpe}")
        response_data["final_message"] = "⚠️ Your request was blocked. Please rephrase your input."
        response_data["raw_output"] = f"Blocked Prompt: {str(bpe)}"
    except genai.types.generation_types.StopCandidateException as sce:
        logging.warning(f"AI generation stopped unexpectedly: {sce}")
        response_data["final_message"] = "⚠️ AI response incomplete. Please try a different phrasing."
        response_data["raw_output"] = f"Stop Candidate: {str(sce)}"
    except Exception as e:
        logging.exception("Unexpected error during emotion mapping.")
        response_data["final_message"] = f"⚠️ An unexpected error occurred: {html.escape(str(e))}"
        response_data["raw_output"] = f"Exception: {html.escape(str(e))}"

    return render_template("index.html", **response_data)

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        logging.critical("FATAL: GEMINI_API_KEY not set. Application cannot reliably start.")
    elif not model:
        logging.critical(f"FATAL: Generative model '{MODEL_NAME}' failed to initialize. Application cannot reliably start.")
    

    app.run(debug=True, host='0.0.0.0', port=5001)