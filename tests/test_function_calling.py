from google import genai
from google.genai import types

# Define the function declaration for the model
get_weather_scheme = {
    "name": "get_weather",
    "description": "Узнать текущую погоду в указанном городе.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Город, для которого нужна погода. Например: Москва",
            },
        },
    },
}


# Configure the client and tools
client = genai.Client()
tools = types.Tool(function_declarations=[get_weather_scheme])
config = types.GenerateContentConfig(tools=[tools])

# Send request with function declarations
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Schedule a meeting with Bob and Alice for 03/14/2025 at 10:00 AM about the Q3 planning.",
    config=config,
)

# Check for a function call
if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    print(f"Function to call: {function_call.name}")
    print(f"Arguments: {function_call.args}")
    #  In a real app, you would call your function here:
    #  result = schedule_meeting(**function_call.args)
else:
    print("No function call found in the response.")
    print(response.text)