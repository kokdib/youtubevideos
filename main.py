import re
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Set up YouTube Data API credentials
API_KEY = 'API_KEY'  # Replace with your own API key


# Function to retrieve channel ID from username
def get_channel_id(username):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    try:
        # Search for channels with the given username
        response = youtube.search().list(part='snippet', q=username, type='channel', maxResults=1).execute()
        channel_id = response['items'][0]['id']['channelId']
        return channel_id

    except HttpError as e:
        st.error(f'Error retrieving channel ID: {e}')


# Function to extract channel ID or username from YouTube channel link
def extract_channel_info(link):
    # Extract channel ID or username from the link using regex
    pattern = r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:channel\/|@)?([a-zA-Z0-9_-]{1,})"
    match = re.search(pattern, link)

    if match:
        channel_info = match.group(1)
        return channel_info

    return None


# Function to retrieve videos from a YouTube channel
def get_channel_videos(channel_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    try:
        # Retrieve playlist ID for uploaded videos
        response = youtube.channels().list(part='contentDetails', id=channel_id).execute()
        playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Retrieve videos from the playlist
        videos = []
        next_page_token = None

        while True:
            response = youtube.playlistItems().list(part='snippet', playlistId=playlist_id,
                                                   maxResults=50, pageToken=next_page_token).execute()

            videos.extend(response['items'])
            next_page_token = response.get('nextPageToken')

            if not next_page_token:
                break

        return videos

    except HttpError as e:
        st.error(f'Error retrieving videos: {e}')


# Streamlit app
def main():
    st.title("YouTube Channel Videos")

    # Input channel ID, username, or YouTube channel link
    channel_input = st.text_input("Enter YouTube channel ID, username, or channel link")

    if st.button("Search"):
        # Retrieve videos and display
        if channel_input:
            # Check if input is channel ID, username, or link
            if channel_input.startswith('UC'):
                channel_id = channel_input  # Input is already a channel ID
            elif channel_input.startswith('@'):
                username = channel_input[1:]  # Remove '@' from the beginning of the username
                channel_id = get_channel_id(username)
            else:
                # Input is YouTube channel link, extract channel info
                channel_info = extract_channel_info(channel_input)

                if channel_info:
                    if channel_info.startswith('UC'):
                        channel_id = channel_info  # Extracted info is channel ID
                    else:
                        username = channel_info  # Extracted info is username
                        channel_id = get_channel_id(username)
                else:
                    st.warning("Invalid YouTube channel link or input format")

            if channel_id:
                videos = get_channel_videos(channel_id)

                if videos:
                    st.success(f"Found {len(videos)} videos")
                    for video in videos:
                        title = video['snippet']['title']
                        video_id = video['snippet']['resourceId']['videoId']
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        st.write(f"- [{title}]({video_url})")
                else:
                    st.warning("No videos found for the channel ID or username")
            else:
                st.warning("No channel found for the channel ID or username")
        else:
            st.warning("Please enter a valid YouTube channel ID, username, or channel link")


if __name__ == "__main__":
    main()
