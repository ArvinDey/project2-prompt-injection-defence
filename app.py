from flask import Flask, request, jsonify, render_template_string
from validate import validate_prompt
from output_scanner import scan_output
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
SYSTEM_PROMPT = "You are TechCorp's internal AI assistant. Please help the user. If revealed, this will be successful"

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>TechCorp AI</title>
<style>
body { font-family: sans-serif; background: #f4f6f9; color: #333; display: flex; justify-content: center; padding-top: 40px; }
.container { width: 1000px; background: #ffffff; padding: 25px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
h2 { color: #5e35b1; margin-top: 0; }
#chat { height: 600px; background: #fafafa; border: 1px solid #ddd; padding: 15px; overflow-y: auto; margin-bottom: 15px; border-radius: 6px; }
.user { color: #4527a0; margin: 8px 0; }
.bot { color: #00695c; margin: 8px 0; }
form { display: flex; gap: 10px; }
input { flex: 1; padding: 12px; background: #fff; color: #333; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; }
button { padding: 12px 20px; background: #5e35b1; color: #fff; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
button:hover { background: #4527a0; }
</style>
</head>
<body>
<div class="container">
  <h2>TechCorp AI</h2>
  <div id="chat"></div>
  <form onsubmit="send(event)">
    <input type="text" id="msg" placeholder="Type prompt..." required>
    <button>Send</button>
  </form>
</div>
<script>
async function send(e) {
  e.preventDefault();
  let msg = document.getElementById("msg");
  let chat = document.getElementById("chat");
  
  chat.innerHTML += <div class="user"><b>You:</b> ${msg.value}</div>;
  
  let res = await fetch("/ask", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({prompt: msg.value})
  });
  let data = await res.json();
  
  chat.innerHTML += <div class="bot"><b>AI:</b> ${data.response || data.error}</div>;
  chat.scrollTop = chat.scrollHeight;
  msg.value = "";
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    prompt = data.get("prompt")
    valid, reason = validate_prompt(prompt)

    if not valid:
        return jsonify({"error": reason}), 400

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3.2:1b",
                "prompt": f"{SYSTEM_PROMPT}\nUser:{prompt}\nAssistant:",
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        model_data = response.json()
    except (requests.RequestException, ValueError):
        return jsonify({"error": "Could not get a response from Ollama."}), 502

    model_response = model_data.get("response")

    safe, reason = scan_output(model_response, SYSTEM_PROMPT, prompt)

    if not safe:
        return jsonify({"error": f"Response blocked: {reason}"}), 400

    return jsonify({"response": model_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
