from PIL import Image
import os
import argparse

def convert_image_for_youtube(input_image, output_image, resize_x = 1280, resize_y = 720, output_format="JPEG"):
    """
    Convert an image to YouTube-friendly format (JPEG, 1280x720).
    """
    try:
        img = Image.open(input_image)
        # Resize to 1280x720 (16:9)
        img = img.resize((resize_x, resize_y), Image.Resampling.LANCZOS)
        # Save as JPEG
        img.save(output_image, format=output_format)
        print(f"✅ Converted {input_image} → {output_image}")
    except Exception as e:
        print("❌ Error converting image:", e)

def main():
    parser = argparse.ArgumentParser(description="Resize and convert image for YouTube thumbnails.")
    parser.add_argument("song_name", help="Name of the somng to identify each project for data and output.")
    parser.add_argument("input_image_name", help="Path to the input image file.")
    parser.add_argument("output_image_name", help="Path to save the converted image file.")
    parser.add_argument("--width", type=int, default=1280, help="Width of the output image (default: 1280).")
    parser.add_argument("--height", type=int, default=720, help="Height of the output image (default: 720).")
    args = parser.parse_args()

    data_rel_path = os.path.join('..', '..', 'data', args.song_name)
    output_rel_path = os.path.join('..', '..', 'output', args.song_name)
    os.makedirs(output_rel_path, exist_ok=True)
    args.input_image =  os.path.join(data_rel_path, args.input_image_name)
    args.output_image = os.path.join(output_rel_path, args.output_image_name)

    convert_image_for_youtube(args.input_image, args.output_image, args.width, args.height)

if __name__ == "__main__":
    main()