import replicate
import os

client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

def generate_image(prompt):
    try:
        output = client.run(
            "stability-ai/sdxl:latest",
            input={"prompt": prompt}
        )
        return output[0] if output else None
    except Exception as e:
        print(f"[ERROR] Replicate: {e}")
        return None