import os
import json
from openai import AzureOpenAI

def get_azure_openai_response(endpoint, deployment, subscription_key, chat_prompt):
    # Initialize Azure OpenAI client with key-based authentication
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=subscription_key,
        api_version="2025-01-01-preview",
    )

    # Generate the completion
    completion = client.chat.completions.create(
        model=deployment,
        messages=chat_prompt,
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )

    # Extract the content from the response
    import json
    json_response = completion.to_json()
    response_data = json.loads(json_response)

    content = response_data["choices"][0]["message"]["content"]
    return content

# Define your parameters
endpoint = os.getenv("ENDPOINT_URL", "https://ridwa-mcn8ojtg-swedencentral.cognitiveservices.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "1H2kv64mGcuOzr3gMOpYqxO6ZI76dUOyn7XUMKFXa4TVqvONhqxbJQQJ99BGACfhMk5XJ3w3AAAAACOGrsbU")

# Prepare the chat prompt
chat_prompt = [
    {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": """ 
                ('Disini kamu sebagai AI Assistant BranchBank Mandiri KCP Jakarta Ancol akan membantu menjawab pertanyaan terkait performa cabang Bank Mandiri. Kamu akan menjawab pertanyaan berdasarkan data List-Review dibawah ini.\n\n\n\n', 'Place Name,Star Rating,Review Content,Sentiment\nBank Mandiri KCP Jakarta Ancol,5,buka rek untuk nabung cepat dan kary ramah,2\nBank Mandiri KCP Jakarta Ancol,5,pembuatan rekening cepat dan petugasnya oke,2\nBank Mandiri KCP Jakarta Ancol,5,pembuatan tabungan dibantu sekuriti ramah dan cepat,2\nBank Mandiri KCP Jakarta Ancol,5,anda memberikan layanan yang sangat baik,2\nBank Mandiri KCP Jakarta Ancol,5,sangat puas pelayanannya,2\nBank Mandiri KCP Jakarta Ancol,5,"pelayanannya cepat, mudah dan enggak ribet. thank you bu nurhayati atas pelayanannya",2\nBank Mandiri KCP Jakarta Ancol,5,pelayanannya oke,2\nBank Mandiri KCP Jakarta Ancol,5,rama ramah,2\nBank Mandiri KCP Jakarta Ancol,5,bersih dan ramah sekali cs tellernya,2\nBank Mandiri KCP Jakarta Ancol,5,sangat puas dengan pelayanan yang diberikan.,2\nBank Mandiri KCP Jakarta Ancol,5,mantap,2\nBank Mandiri KCP Jakarta Ancol,5,pelayanannya bagus,2\nBank Mandiri KCP Jakarta Ancol,5,"pegawainya semua ramah-ramah, terutama bu nur hayati yang melayani say\n\n', "Pertanyaan : Berikan ringkasan performanya'"""
            }
        ]
    }
]

# Call the function and print the response
response_content = get_azure_openai_response(endpoint, deployment, subscription_key, chat_prompt)
print(response_content)
