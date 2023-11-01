from PIL import Image, ImageSequence
import os

# Path to the GIF file
gif_path = "photos/Dancing-cow.gif"
output_dir = "photos/cow-gif"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load the GIF and extract frames
gif = Image.open(gif_path)
frames = [frame.copy() for frame in ImageSequence.Iterator(gif)]

# Save frames as PNG images
for i, frame in enumerate(frames):
    # Adjust the output file path format, e.g., "frame_001.png", "frame_002.png", ...
    output_file = os.path.join(output_dir, f"frame_{i + 1:03d}.png")
    frame.save(output_file, "PNG")

print("Frames extracted and saved to PNG files in", output_dir)
