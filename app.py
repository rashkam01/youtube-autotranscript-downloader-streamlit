import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from googletrans import Translator

def get_video_id(url):
    """Extracts the video ID from the YouTube URL."""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "youtube.com/live/" in url:
        return url.split("/live/")[1].split("?")[0]
    else:
        return None

def get_transcript(video_id):
    """Fetches the transcript in Gujarati ('gu'), or translates from Hindi ('hi') if needed."""
    translator = Translator()

    try:
        # Try fetching the Gujarati transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["gu"])
        return "\n".join([entry['text'] for entry in transcript])  # Return Gujarati transcript directly
    
    except NoTranscriptFound:
        # If Gujarati is not available, try fetching Hindi transcript
        try:
            transcript_hi = YouTubeTranscriptApi.get_transcript(video_id, languages=["hi"])
            hindi_text = "\n".join([entry['text'] for entry in transcript_hi])  # Get Hindi text
            
            # Translate Hindi to Gujarati
            translated_text = translator.translate(hindi_text, src="hi", dest="gu").text
            return translated_text  # Return translated Gujarati text
        
        except NoTranscriptFound:
            return "No transcript found in Gujarati or Hindi."
    
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.title("YouTube Transcript Extractor 🎬📜")
st.write("Enter a YouTube video URL to get its auto-generated transcript.")

# User Input
video_url = st.text_input("Paste YouTube URL here:", "")

if st.button("Get Transcript"):
    if video_url:
        video_id = get_video_id(video_url)
        if video_id:
            st.info("Fetching transcript... Please wait.")
            transcript_text = get_transcript(video_id)
            st.text_area("Gujarati Transcript:", transcript_text, height=300)  # Display transcript
        else:
            st.error("Invalid YouTube URL. Please check and try again.")
    else:
        st.warning("Please enter a valid YouTube URL.")

# import streamlit as st
# from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# def get_video_id(url):
#     """Extracts the video ID from the YouTube URL."""
#     if "v=" in url:
#         return url.split("v=")[1].split("&")[0]
#     elif "youtu.be/" in url:
#         return url.split("youtu.be/")[1].split("?")[0]
#     elif "youtube.com/live/" in url:
#         return url.split("/live/")[1].split("?")[0]
#     else:
#         return None

# def get_transcript(video_id, language="gu"):
#     """Fetches the transcript for the given video ID."""
#     try:
#         transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
#         return "\n".join([entry['text'] for entry in transcript])  # Join transcript text
#     except TranscriptsDisabled:
#         return "Transcripts are disabled for this video."
#     except NoTranscriptFound:
#         return "No transcript found in the selected language."
#     except Exception as e:
#         return f"Error: {e}"

# # Streamlit UI
# st.title("YouTube Transcript Extractor 🎬📜")
# st.write("Enter a YouTube video URL to get its auto-generated transcript.")

# # User Input
# video_url = st.text_input("Paste YouTube URL here:", "")

# if st.button("Get Transcript"):
#     if video_url:
#         video_id = get_video_id(video_url)
#         if video_id:
#             st.info("Fetching transcript... Please wait.")
#             transcript_text = get_transcript(video_id, language="gu")
#             st.text_area("Transcript:", transcript_text, height=300)  # Display transcript in a text box
#         else:
#             st.error("Invalid YouTube URL. Please check and try again.")
#     else:
#         st.warning("Please enter a valid YouTube URL.")


# import streamlit as st
# from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
# import yt_dlp
# import re

# def get_video_id(url):
#     """Extracts the video ID from the YouTube URL."""
#     if "v=" in url:
#         return url.split("v=")[1].split("&")[0]
#     elif "youtu.be/" in url:
#         return url.split("youtu.be/")[1].split("?")[0]
#     elif "youtube.com/live/" in url:
#         return url.split("/live/")[1].split("?")[0]
#     else:
#         return None

# def sanitize_filename(filename, max_length=25):
#     """Removes invalid characters and truncates the filename to 25 characters."""
#     filename = re.sub(r'[<>:"/\\|?*]', '_', filename)  # Replace invalid characters with '_'
#     return filename[:max_length]  # Limit filename to 25 characters

# def get_video_title(video_url):
#     """Fetches and sanitizes the title of the YouTube video."""
#     try:
#         ydl_opts = {"quiet": True}
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(video_url, download=False)
#             title = info.get("title", "Unknown_Video")
#             return sanitize_filename(title)  # Truncate title to 25 characters
#     except Exception:
#         return "Unknown_Video"

# def get_transcript(video_id, language="gu"):
#     """Fetches the transcript for the given video ID."""
#     try:
#         transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
#         return "\n".join([entry['text'] for entry in transcript])  # Join transcript text
#     except TranscriptsDisabled:
#         return "Transcripts are disabled for this video."
#     except NoTranscriptFound:
#         return "No transcript found in the selected language."
#     except Exception as e:
#         return f"Error: {e}"

# # Streamlit UI
# st.title("YouTube Transcript Extractor 🎬📜")
# st.write("Enter a YouTube video URL to get its auto-generated transcript.")

# # User Input
# video_url = st.text_input("Paste YouTube URL here:", "")

# if st.button("Get Transcript"):
#     if video_url:
#         video_id = get_video_id(video_url)
#         if video_id:
#             st.info("Fetching video title and transcript... Please wait.")
            
#             video_title = get_video_title(video_url)
#             transcript_text = get_transcript(video_id, language="gu")

#             # Save transcript as a file
#             output_file = f"{video_title}_transcript.txt"
#             with open(output_file, "w", encoding="utf-8") as file:
#                 file.write(transcript_text)

#             st.success(f"Gujarati transcript saved as: `{output_file}`")
#             st.text_area("Transcript:", transcript_text, height=300)
#         else:
#             st.error("Invalid YouTube URL. Please check and try again.")
#     else:
#         st.warning("Please enter a valid YouTube URL.")




# import streamlit as st
# from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
# import yt_dlp

# def get_video_id(url):
#     """Extracts the video ID from the YouTube URL."""
#     if "v=" in url:
#         return url.split("v=")[1].split("&")[0]
#     elif "youtu.be/" in url:
#         return url.split("youtu.be/")[1].split("?")[0]
#     elif "youtube.com/live/" in url:
#         return url.split("/live/")[1].split("?")[0]
#     else:
#         return None

# def get_video_title(video_url):
#     """Fetches the title of the YouTube video."""
#     try:
#         ydl_opts = {"quiet": True}
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(video_url, download=False)
#             return info.get("title", "Unknown_Title")
#     except Exception as e:
#         return f"Error fetching title: {e}"

# def get_transcript(video_id, language="gu"):
#     """Fetches the transcript for the given video ID."""
#     try:
#         transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
#         return "\n".join([entry['text'] for entry in transcript])  # Join transcript text
#     except TranscriptsDisabled:
#         return "Transcripts are disabled for this video."
#     except NoTranscriptFound:
#         return "No transcript found in the selected language."
#     except Exception as e:
#         return f"Error: {e}"

# # Streamlit UI
# st.title("YouTube Transcript Extractor 🎬📜")
# st.write("Enter a YouTube video URL to get its auto-generated transcript.")

# # User Input
# video_url = st.text_input("Paste YouTube URL here:", "")

# if st.button("Get Transcript"):
#     if video_url:
#         video_id = get_video_id(video_url)
#         if video_id:
#             st.info("Fetching video title and transcript... Please wait.")
            
#             video_title = get_video_title(video_url)
#             sanitized_title = video_title.replace(" ", "_").replace("/", "_")  # Clean filename

#             transcript_text = get_transcript(video_id, language="gu")

#             # Save transcript as a file
#             output_file = f"{sanitized_title}_transcript.txt"
#             with open(output_file, "w", encoding="utf-8") as file:
#                 file.write(transcript_text)

#             st.success(f"Gujarati transcript saved as: `{output_file}`")
#             st.text_area("Transcript:", transcript_text, height=300)
#         else:
#             st.error("Invalid YouTube URL. Please check and try again.")
#     else:
#         st.warning("Please enter a valid YouTube URL.")

# import streamlit as st
# from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
# import yt_dlp
# import re

# def get_video_id(url):
#     """Extracts the video ID from the YouTube URL."""
#     if "v=" in url:
#         return url.split("v=")[1].split("&")[0]
#     elif "youtu.be/" in url:
#         return url.split("youtu.be/")[1].split("?")[0]
#     elif "youtube.com/live/" in url:
#         return url.split("/live/")[1].split("?")[0]
#     else:
#         return None

# def sanitize_filename(filename):
#     """Removes invalid characters from a filename."""
#     return re.sub(r'[<>:"/\\|?*]', '_', filename)  # Replace invalid characters with '_'

# def get_video_title(video_url):
#     """Fetches the title of the YouTube video, handling errors properly."""
#     try:
#         ydl_opts = {"quiet": True}
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(video_url, download=False)
#             title = info.get("title", "Unknown_Title")
#             return sanitize_filename(title)  # Sanitize title for filename safety
#     except Exception as e:
#         return "Unknown_Video"  # Use a default title if fetching fails

# def get_transcript(video_id, language="gu"):
#     """Fetches the transcript for the given video ID."""
#     try:
#         transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
#         return "\n".join([entry['text'] for entry in transcript])  # Join transcript text
#     except TranscriptsDisabled:
#         return "Transcripts are disabled for this video."
#     except NoTranscriptFound:
#         return "No transcript found in the selected language."
#     except Exception as e:
#         return f"Error: {e}"

# # Streamlit UI
# st.title("YouTube Transcript Extractor 🎬📜")
# st.write("Enter a YouTube video URL to get its auto-generated transcript.")

# # User Input
# video_url = st.text_input("Paste YouTube URL here:", "")

# if st.button("Get Transcript"):
#     if video_url:
#         video_id = get_video_id(video_url)
#         if video_id:
#             st.info("Fetching video title and transcript... Please wait.")
            
#             video_title = get_video_title(video_url)
#             transcript_text = get_transcript(video_id, language="gu")

#             # Save transcript as a file
#             output_file = f"{video_title}_transcript.txt"
#             with open(output_file, "w", encoding="utf-8") as file:
#                 file.write(transcript_text)

#             st.success(f"Gujarati transcript saved as: `{output_file}`")
#             st.text_area("Transcript:", transcript_text, height=300)
#         else:
#             st.error("Invalid YouTube URL. Please check and try again.")
#     else:
#         st.warning("Please enter a valid YouTube URL.")
