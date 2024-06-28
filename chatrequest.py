from openai import OpenAI
import os
import ast

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def test_response(caption_clean):
    sys_prompt = "This is the caption Instagram reel that is recommending one or more places to eat. Using the information provided and other info on the web, return the recommendations as a list of lists in the format of [[\"name1\", \"location1\", \"city1\", \"cuisine1\"], [\"name2\", \"location2\", \"city2\", \"cuisine2\"]]. If there is just a single recommendation, still return that list within a list []. For location, have it in the format of street number, city, state, zip code. For city, give the full city name, formatted correctly. For example you would return New York instead of New York City, unless City is part of the official city name like Michigan City. For cuisine, return a single word (example: Chinese, Japanese, Italian, etc). Return the list of lists only - no additional text. If you can find any one of the name, location, city, or cuisine, don't include the list for recommendation in the list of lists. If there isn't enough info to find the restaraunt, just return the word false"

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": caption_clean}
        ],
    )
    
    response = completion.choices[0].message.content
    if response.strip("'").lower == "false":
        list_response = [["false", "false,", "false", "false"]]
    else:
        list_response = ast.literal_eval(response)
    return list_response

def get_response(prompt):
    sys_prompt = "This is the caption and transcription of an Instagram reel that is recommending one or more places to eat. Using the information provided and other info on the web, return the recommendations as a list of lists in the format of [[\"name1\", \"location1\", \"city1\", \"cuisine1\"], [\"name2\", \"location2\", \"city2\", \"cuisine2\"]]. If there is just a single recommendation, still return that list within a list []. For location, have it in the format of street number, city, state, zip code. For city, give the full city name, formatted correctly. For example you would return New York instead of New York City, unless City is part of the official city name like Michigan City. For cuisine, return a single word (example: Chinese, Japanese, Italian, etc). Return the list of lists only - no additional text. If you can find any one of the name, location, city, or cuisine, don't include the list for recommendation in the list of lists"

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
    )

    response = completion.choices[0].message.content
    list_response = ast.literal_eval(response)
    return list_response