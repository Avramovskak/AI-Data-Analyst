import ollama

print("Connecting to local Llama...")

response = ollama.chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful data analyst."
        },
        {
            "role": "user",
            "content": "What is SQL? Explain it in one sentence."
        }
    ]
)

print("\nLlama response:")
print(response["message"]["content"])