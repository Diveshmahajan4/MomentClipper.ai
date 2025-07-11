import openai
from dotenv import load_dotenv
import os
import json
import logging

logger = logging.getLogger(__name__)

load_dotenv()

openai.api_key = os.getenv("OPENAI_API")

num_highlights = 1

if not openai.api_key:
    raise ValueError("API key not found. Make sure it is defined in the .env file.")


def extract_times(json_string):
    try:

        data = json.loads(json_string)

        start_time = float(data[0]["start"])
        end_time = float(data[0]["end"])

        start_time_int = int(start_time)
        end_time_int = int(end_time)
        return start_time_int, end_time_int
    except Exception as e:
        print(f"Error in extract_times: {e}")
        return 0, 0



system = """

Baised on the Transcription user provides with start and end, Highilight the main parts in less then 1 min which can be directly converted into a short. highlight it such that its intresting and also keep the time staps for the clip to start and end. only select a continuous part of the video

Follow this Format and return in valid json 
[{
start: "Start time of the clip",
content: "Highlight Text",
end: "End Time for the highlighted clip"
}]
it should be one continuous clip as it will then be cut from the video and uploaded as a tiktok video. so only have one start, end and content

Dont say anything else, just return Proper Json. no explanation etc


IF YOU DONT HAVE ONE start AND end WHICH IS FOR THE LENGTH OF THE ENTIRE HIGHLIGHT, THEN 10 KITTENS WILL DIE, I WILL DO JSON['start'] AND IF IT DOESNT WORK THEN...
"""

def get_system_prompt(num_highlights):
    system_prompt = f"""
        Based on the transcription user provides with start and end timestamps, identify exactly {num_highlights} interesting highlights that can be converted into separate short videos. highlight it such that its intresting and also keep the time staps for the clip to start and end. only select a continuous part of the video

        Return a JSON array with exactly {num_highlights} highlights. Each highlight should have this exact format:
        [
            {{
                start: "Start time of the clip",
                content: "Highlight Text",
                end: "End Time for the highlighted clip"
            }}
        ]

        IMPORTANT RULES:
        - Return exactly {num_highlights} highlights
        - Each highlight must be 60 seconds long
        - No overlapping time ranges between highlights
        - Each highlight should cover different topics/themes for variety
        - Return ONLY valid JSON, no explanations or additional text
        - If there aren't enough distinct segments, return as many as possible

        CRITICAL: Each highlight must have exactly one start time and one end time for a continuous segment that will be cut from the video.
    """
    return system_prompt

User = """
Any Example
"""


def GetHighlight(Transcription):
    print("Getting Highlight from Transcription ")
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": Transcription + system},
            ],
        )

        json_string = response.choices[0].message.content
        json_string = json_string.replace("json", "").replace("```", "")
        print("Json String: ", json_string)
        Start, End = extract_times(json_string)
        if Start == End:
            # Retry up to 3 times automatically
            for i in range(3):
                print(f"Retrying highlight extraction (attempt {i+1}/3)")
                response = client.chat.completions.create(
                    model="gpt-4o",
                    temperature=0.7 + (i * 0.1),  
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": Transcription + system},
                    ],
                )
                json_string = response.choices[0].message.content
                json_string = json_string.replace("json", "").replace("```", "")
                Start, End = extract_times(json_string)
                if Start != End:
                    break
        return Start, End

    except Exception as e:
        print(f"Error in GetHighlight: {e}")
        return 0, 0
    
def getMultipleHighlights(Transcription, num_highlights):
    print("Getting Multiple Highlights from Transcription ")
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API"))
    
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": get_system_prompt(num_highlights)},
                {"role": "user", "content": Transcription + get_system_prompt(num_highlights)},
            ],
        )

        json_string = response.choices[0].message.content
        json_string = json_string.replace("json", "").replace("```", "")
        print("Json String: ", json_string)
        return json_string

    except Exception as e:
        print(f"Error in GetHighlight: {e}")
        return 0, 0

if __name__ == "__main__":
    print(GetHighlight(User))
