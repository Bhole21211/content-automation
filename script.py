
import os
import requests
import zipfile
import re
import time

# WordPress credentials and endpoints
WORDPRESS_URL = "https://bholesinghprivatelimited.online"
API_ENDPOINT = f"{WORDPRESS_URL}/wp-json/wp/v2/posts"
MEDIA_ENDPOINT = f"{WORDPRESS_URL}/wp-json/wp/v2/media"
USERNAME = "bholesingh454@gmail.com"  # Replace with your WordPress username
PASSWORD = "uMzI Ts1h kjCg rr42 CqWq 4pDg"  # Replace with your application password

# API Keys
CONTENT_API_KEY = "AIzaSyA3pVFeh0lbm558doJmCDOt2jvc6tFDJBo"  # Replace with your content generation API key
IMAGE_API_KEY = "s4i9qlH9Zw1jmxB20ilOTpwHxk6RocpCfWWEboNsCNfJm3QWIRXR7MNM"  # Replace with your Pexels API key

# Function to generate content using API
def generate_content(heading):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={CONTENT_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Write a detailed, unique, and comprehensive article on '{heading}' without using any star symbols (*, **, ***). "
                            f"Ensure the content is structured professionally with headings, subheadings, and bullet points. "
                            f"Include SEO keywords, meta descriptions, tags, and a well-formatted introduction and conclusion. "
                            f"The content should be at least 8,000 words long with real-world examples, case studies, and statistics. "
                            f"Make the article engaging, informative, and written in perfect English."
                        )
                    }
                ]
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        candidates = response_json.get("candidates", [])
        if candidates:
            content_parts = candidates[0].get("content", {}).get("parts", [])
            if content_parts:
                return re.sub(r'\*+', '', "\n\n".join([part.get("text", "") for part in content_parts]))
    return "Error generating content."

# Function to get an image URL using Pexels API
def get_image_url(search_query):
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": IMAGE_API_KEY}
    params = {"query": search_query, "per_page": 1}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["photos"]:
            return data["photos"][0]["src"]["original"]
    return None

# Function to upload featured image and get its ID
def upload_featured_image(image_url):
    try:
        image_name = image_url.split("/")[-1]
        headers = {"Content-Disposition": f"attachment; filename={image_name}"}
        response = requests.get(image_url)
        if response.status_code == 200:
            files_data = {"file": (image_name, response.content, "image/jpeg")}
            media_response = requests.post(MEDIA_ENDPOINT, headers=headers, files=files_data, auth=(USERNAME, PASSWORD))
            if media_response.status_code == 201:
                return media_response.json().get("id")
    except Exception as e:
        print(f"Error uploading image: {e}")
    return None

# Function to create a post on WordPress with SEO metadata
def create_post(title, content, featured_image_url):
    data = {
        "title": title, 
        "content": f"<strong>{content}</strong>", 
        "status": "publish",
        "meta": {
            "seo_keywords": title,
            "seo_meta_description": f"Comprehensive article about {title} with real-world examples and detailed analysis.",
            "tags": [title]
        }
    }
    if featured_image_url:
        image_id = upload_featured_image(featured_image_url)
        if image_id:
            data["featured_media"] = image_id

    response = requests.post(API_ENDPOINT, json=data, auth=(USERNAME, PASSWORD))
    if response.status_code == 201:
        print(f"Post '{title}' created successfully!")
    else:
        print(f"Failed to create post '{title}'. Error: {response.text}")

# Extract ZIP file and process
def extract_and_process_zip(file_name="files.zip"):
    try:
        with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall("uploaded_files")
            print("ZIP file extracted successfully.")
    except FileNotFoundError:
        print(f"{file_name} not found! Please upload the ZIP file.")
        return
    except Exception as e:
        print(f"Error extracting ZIP file: {e}")
        return
    
    # Read TXT files
    txt_files = [f for f in os.listdir("uploaded_files") if f.endswith('.txt')]
    if not txt_files:
        print("No TXT files found!")
        return
    
    for file_name in txt_files:
        file_path = os.path.join("uploaded_files", file_name)
        with open(file_path, "r") as file:
            headings = file.readlines()
        
        for index, heading in enumerate(headings):
            heading = heading.strip()
            if not heading:
                continue

            print(f"Processing Heading {index + 1}: {heading}")

            # Step 1: Generate content
            content = generate_content(heading)
            print(f"Content generated for: {heading}")

            # Step 2: Fetch featured image
            image_url = get_image_url(heading)
            if not image_url:
                print(f"No image found for: {heading}")
                continue

            print(f"Image URL fetched: {image_url}")

            # Step 3: Create post with SEO metadata
            create_post(heading, content, image_url)

# Main process
extract_and_process_zip()

# Keep Script Running
while True:
    time.sleep(60)
    print("Runtime Active...")
