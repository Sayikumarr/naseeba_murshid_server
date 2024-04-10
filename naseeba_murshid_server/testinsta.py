import instaloader

# Create an Instaloader object
loader = instaloader.Instaloader()

# Get the profile posts
profile = instaloader.Profile.from_username(loader.context, "naseeba.murshid")

# Get only the last 25 posts
posts = profile.get_posts()
posts = list(posts)[:25]

# Print the image posts
for post in posts:
    if post.is_video == False:  # Check if the post is not a video
        print(post.url)
    else:
        print("Video Skip!!")