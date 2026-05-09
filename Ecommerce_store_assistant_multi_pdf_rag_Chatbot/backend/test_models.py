# test_models.py
import google.generativeai as genai

# Configure with your API key
genai.configure(api_key="AIzaSyCf2yHiUuwxOAN3bHgwz7j5CUp_shDXUXw")

# List all available models
print("Available models:")
for model in genai.list_models():
    print(f"- {model.name}: {model.supported_generation_methods}")