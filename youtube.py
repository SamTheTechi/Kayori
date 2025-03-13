import os
import re
import requests
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain_google_genai import ChatGoogleGenerativeAI
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("YOU_TUBE")
CHANNEL_IDS = ["UCUyeluBRhGPCW4rPe_UvBZQ", "UCxzC4EngIsMrPmbm6Nxvb-A"]


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.5
)

template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are Kaori, an AI assistant specializing in multi-stage\
        summarization. You are currently processing a {typ}. "
        "Condense long transcripts into clear, concise\
        summaries while preserving key details, emotions, and context. "
        "For chunk summaries, extract essential information,\
        remove repetition, and maintain logical flow. "
        "For the final summary, merge chunks into a seamless,\
        accurate version under 300 words, ensuring readability\
        without losing crucial context. "
        "Avoid introductions, filler, and opinions. Keep it clear,\
        structured, and true to the original content."
    ),
    HumanMessagePromptTemplate.from_template('{data}')
])


def summarizeSentence(data: str, typ: str) -> str:
    prompt = (template | llm).invoke({"data": data, "typ": typ})
    return prompt.content


def latest_videos_transcribe(count: int) -> str:
    if count > 15:
        return None

    for channel_id in CHANNEL_IDS:
        url = f"https://www.googleapis.com/youtube/v3/search?key={
            API_KEY}&channelId={channel_id}&part=snippet&order=date&maxResults={count}"
        response = requests.get(url).json()

        if "items" not in response or not response["items"]:
            continue

        for item in response["items"]:
            video_id = item["id"]["videoId"]

            vid_url = f"https://www.googleapis.com/youtube/v3/videos?key={
                API_KEY}&id={video_id}&part=contentDetails"
            vidcontent = requests.get(vid_url).json()

            if "items" not in vidcontent or not vidcontent["items"]:
                continue

            duration = vidcontent["items"][0]["contentDetails"]["duration"]

            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
            min = int(match.group(2) or 0)
            sec = int(match.group(3) or 0)
            if (min * 60 + sec) > 120:
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(
                        video_id, languages=['en'])
                    text = " ".join([t['text'] for t in transcript])
                    return text
                except Exception as e:
                    return f"No subtitles available. {e}"

    return latest_videos_transcribe(count + 5)


def summrise_transcript(trns: str) -> str:
    if (len(trns) < 15000):
        return summarizeSentence(trns, "chunk summary")
    else:
        words = trns.split()
        chunks = []
        for i in range(0, len(trns), 15000):
            chunks.append(" ".join(words[i:i+15000]))
        chunk_sum = [summarizeSentence(chunk, "chunk summary")
                     for chunk in chunks]
        return summarizeSentence(chunk_sum, "final summary")


print(summrise_transcript(latest_videos_transcribe(5)))
