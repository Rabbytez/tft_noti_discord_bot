from pytubefix import YouTube

def download_video(url):
    try:
        # Create a YouTube object with the URL
        yt = YouTube(url)
        
        # Display video title
        print(f"Title: {yt.title}")

        # Get the highest resolution stream available
        stream = yt.streams.get_highest_resolution()

        # Download the video
        print("Downloading...")
        stream.download()  # By default, downloads to the current working directory
        print("Download completed!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Input YouTube video URL
    video_url = input("Enter the YouTube video URL: ")
    download_video(video_url)
