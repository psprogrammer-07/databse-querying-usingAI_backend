from google import genai

# 1. Initialize the Client
# Replace 'YOUR_API_KEY' with your actual key from Google AI Studio
client = genai.Client(api_key='api')

# 2. Generate Content
response = client.models.generate_content(
    model='gemini-2.0-flash-lite', 
    contents='Explain the benefit of low-latency AI models.'
)

# 3. Print the result

print(response.text)



#AIzaSyBya3aifD6TGgBbQK13g7el80Q529YigJ4