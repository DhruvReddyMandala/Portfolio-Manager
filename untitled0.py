import torch
import torch.nn as nn
from flask import Flask, request, jsonify
from transformers import GPT2Tokenizer

# Define a simple transformer language model from scratch
class SimpleTransformerLanguageModel(nn.Module):
    def __init__(self, vocab_size, embed_size=64, num_heads=2, num_layers=2, hidden_size=128, dropout=0.1):
        super(SimpleTransformerLanguageModel, self).__init__()
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embed_size)
        
        # Transformer block
        self.transformer = nn.Transformer(
            d_model=embed_size,
            nhead=num_heads,
            num_encoder_layers=num_layers,
            num_decoder_layers=num_layers,
            dim_feedforward=hidden_size,
            dropout=dropout
        )
        
        # Output layer to get predictions
        self.fc_out = nn.Linear(embed_size, vocab_size)

    def forward(self, x):
        # Get embeddings for the input
        emb = self.embedding(x)
        
        # Pass through transformer layers
        transformer_out = self.transformer(emb, emb)
        
        # Generate output logits
        logits = self.fc_out(transformer_out)
        return logits

# Initialize Flask app
app = Flask(__name__)

# Initialize the tokenizer (GPT2 tokenizer)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token  # Set padding token as eos_token

# Initialize the model
vocab_size = len(tokenizer)
model = SimpleTransformerLanguageModel(vocab_size)
model.eval()  # Set model to evaluation mode (no gradient updates)

# Initialize conversation history
conversation_history = []

# Function to generate text from the model
def generate_text(prompt, max_length=50):
    # Tokenize the prompt (convert text to token IDs)
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    
    # Generate output from the model
    with torch.no_grad():
        output = model(input_ids)
        predicted_ids = output.argmax(dim=-1)

    # Decode the token IDs back to text
    generated_text = tokenizer.decode(predicted_ids[0], skip_special_tokens=True)
    return generated_text

# Route for chat
@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history
    
    data = request.json
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "Please provide a valid message."}), 400
    
    # Add user's message to conversation history
    conversation_history.append(f"User: {user_message}")
    
    # Concatenate conversation history to use as input for generating context-aware response
    conversation_input = "\n".join(conversation_history)
    
    # Generate AI's response
    ai_response = generate_text(conversation_input)
    
    # Add AI's response to conversation history
    conversation_history.append(f"AI: {ai_response}")
    
    # Return the AI's response
    return jsonify({"response": ai_response})

# Main entry point for running the Flask app locally
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

