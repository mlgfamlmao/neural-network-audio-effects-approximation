import os
import torch
import torch.nn as nn
import torchaudio
import math
import google.generativeai as genai
from dotenv import load_dotenv

# ====================== SETUP ======================
load_dotenv()
# Configure the Google SDK directly with your API key
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ====================== NEURAL NETWORK ARCHITECTURE ======================
class SimpleAudioNN(nn.Module):
    def __init__(self, kernel_size=1): 
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=kernel_size, padding=0),
            nn.ReLU(), 
            nn.Conv1d(16, 32, kernel_size=kernel_size, padding=0),
            nn.ReLU(),
            nn.Conv1d(32, 16, kernel_size=kernel_size, padding=0),
            nn.ReLU(),
            nn.Conv1d(16, 1, kernel_size=kernel_size, padding=0)
        )

    def forward(self, x):
        return self.net(x)

# ====================== LOAD YOUR MODELS ======================
print("Loading neural network weights...")

model_fuzz = SimpleAudioNN(kernel_size=1).to(device)
model_softclip = SimpleAudioNN(kernel_size=5).to(device)
model_wavefold = SimpleAudioNN(kernel_size=1).to(device) 

models = {
    "fuzz": model_fuzz,
    "soft_clip": model_softclip,
    "wave_folding": model_wavefold
}

models["fuzz"].load_state_dict(torch.load("models/fuzz.pth", map_location=device, weights_only=True))
models["soft_clip"].load_state_dict(torch.load("models/SoftClip.pth", map_location=device, weights_only=True))
models["wave_folding"].load_state_dict(torch.load("models/WaveFolding.pth", map_location=device, weights_only=True))

for name, model in models.items():
    model.eval()

# ====================== THE TOOL ======================
# With the Google SDK, tools are just standard Python functions.
# The docstring and type hints are CRITICAL—this is how Gemini knows how to use it!

def apply_distortion(audio_path: str, effect_type: str) -> str:
    """
    Applies a mathematical distortion effect to a .wav audio file and saves the output.
    
    Args:
        audio_path: The exact file path to the user's .wav audio file.
        effect_type: The type of distortion to apply. MUST be 'fuzz', 'soft_clip', or 'wave_folding'.
        
    Returns:
        A string confirming the file was successfully processed and saved, or an error message.
    """
    if effect_type not in models:
        return f"Error: '{effect_type}' is not a valid effect. Use fuzz, soft_clip, or wave_folding."

    try:
        waveform, sample_rate = torchaudio.load(audio_path)
        
        # Convert stereo to mono for the CNN
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        nn_input = waveform.unsqueeze(0).to(device)
        selected_model = models[effect_type]
        
        with torch.no_grad():
            processed_audio = selected_model(nn_input)

        processed_audio = processed_audio.squeeze(0).cpu()
        output_path = audio_path.replace(".wav", f"_{effect_type}_processed.wav")
        torchaudio.save(output_path, processed_audio, sample_rate)
        
        return f"Success! Saved processed audio to: {output_path}"
    
    except Exception as e:
        return f"Error applying distortion: {str(e)}"


# ====================== GEMINI BOT SETUP ======================

# 1. Initialize the model and pass it your Python function
llm = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    tools=[apply_distortion],
    system_instruction=(
        "You are a helpful AI Audio Engineering Assistant called Distort-o-Matic. "
        "You can explain DSP concepts, audio distortion, and neural networks. "
        "If the user asks you to apply an effect to an audio file, use your apply_distortion tool. "
        "Always be friendly, educational, and explain the sonic characteristics of the effect you just applied."
    )
)

# 2. Start a chat session. This natively handles conversation memory!
# enable_automatic_function_calling=True means the SDK will run your Python code automatically behind the scenes.
chat = llm.start_chat(enable_automatic_function_calling=True)

# ====================== CREATE TEST AUDIO ======================
test_file = "test_audio.wav"
if not os.path.exists(test_file):
    print("Generating 3-second test tone...")
    sr = 44100
    t = torch.arange(sr * 3).float() / sr
    sine_wave = 0.5 * torch.sin(2 * math.pi * 440.0 * t).unsqueeze(0) 
    torchaudio.save(test_file, sine_wave, sr)

# ====================== RUN THE CHAT LOOP ======================
if __name__ == "__main__":
    print(f"\n🎸 Distort-o-Matic is ready!")
    print(f"I created a test file for you: {test_file}")
    print("Ask a question like: 'How does soft clipping work mathematically?'")
    print("Or trigger the model: 'Can you add fuzz to test_audio.wav?'")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        try:
            # Send the message. 
            # If Gemini decides to use the tool, the SDK executes your Python function silently,
            # reads the return string, and then hands the result back to Gemini to generate a response.
            response = chat.send_message(user_input)
            print(f"\nDistort-o-Matic: {response.text}\n")
            
        except Exception as e:
            print(f"\nAPI Error: {e}\n")