import requests

# This is the URL of the API endpoint
api_url = "https://jsonplaceholder.typicode.com/posts"

# Make a GET request to the API endpoint
response = requests.get(api_url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response as JSON
    posts = response.json()

    # Display the posts
    print("Received posts:")
    for post in posts:
        print(f"Title: {post['title']}\nBody: {post['body']}\n")
else:
    print(f"Failed to retrieve posts. Status code: {response.status_code}")
