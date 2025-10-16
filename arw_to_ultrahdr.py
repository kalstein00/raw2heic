import argparse
import os
import sys

ULTRAHDR_APP_PATH = './libultrahdr/build/ultrahdr_app'

def main():
    parser = argparse.ArgumentParser(description="Convert Sony ARW files to Ultra HDR.")
    parser.add_argument("input_file", help="Path to the input ARW file.")
    parser.add_argument("output_file", help="Path to the output Ultra HDR file (.hif).")
    parser.add_argument(
        "--keep-intermediates",
        action="store_true",
        help="Keep intermediate SDR and HDR files.",
    )
    args = parser.parse_args()

    print(f"Input file: {args.input_file}")
    print(f"Output file: {args.output_file}")
    print(f"Keep intermediates: {args.keep_intermediates}")

    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found at {args.input_file}", file=sys.stderr)
        sys.exit(1)

    # Create intermediate file paths
    base_name = os.path.splitext(os.path.basename(args.input_file))[0]
    sdr_path = f"{base_name}_sdr.jpg"
    hdr_path = f"{base_name}_hdr.tiff"

    # Process ARW file
    try:
        import rawpy
        import imageio
        import numpy as np
        import subprocess

        print(f"Processing {args.input_file}...")
        with rawpy.imread(args.input_file) as raw:
            # Get image dimensions
            width, height = raw.sizes.width, raw.sizes.height

            # Create SDR image
            print("Creating SDR image...")
            sdr_image = raw.postprocess(
                gamma=(2.4, 12.92), output_bps=8, use_camera_wb=True, output_color=rawpy.ColorSpace.sRGB
            )
            imageio.imwrite(sdr_path, sdr_image, format='JPEG')
            print(f"SDR image saved to {sdr_path}")

            # Create HDR image (16-bit TIFF)
            print("Creating HDR image (TIFF)...")
            hdr_image_tiff = raw.postprocess(
                gamma=(1, 1), output_bps=16, use_camera_wb=True, output_color=rawpy.ColorSpace.ProPhoto
            )
            imageio.imwrite(hdr_path, hdr_image_tiff, format='TIFF')
            print(f"HDR TIFF image saved to {hdr_path}")

            # Convert HDR TIFF to raw format (RGBA Half Float) for ultrahdr_app
            import imageio_ffmpeg
            hdr_raw_path = f"{base_name}_hdr.raw"
            print(f"Converting HDR TIFF to {hdr_raw_path}...")
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            ffmpeg_cmd = [
                ffmpeg_exe, '-i', hdr_path, '-f', 'image2', '-pix_fmt', 'rgba64le', '-vcodec', 'rawvideo', '-y', hdr_raw_path
            ]
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            print("Conversion to raw complete.")

            # Encode with ultrahdr_app
            print("Encoding to Ultra HDR...")
            # We use encoding scenario 3: HDR raw + SDR compressed
            # -p: raw hdr intent, -i: compressed sdr intent, -a: hdr color format, -w: width, -h: height, -z: output
            # color format 4 corresponds to rgbahalffloat
            cmd = [
                ULTRAHDR_APP_PATH,
                '-m', '0',
                '-p', hdr_raw_path,
                '-i', sdr_path,
                '-w', str(width),
                '-h', str(height),
                '-a', '4', # 4 == rgbahalffloat
                '-t', '0', # 0 == linear color transfer
                '-z', args.output_file,
            ]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("Ultra HDR encoding complete.")
            print("ultrahdr_app output:", result.stdout)


    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        if hasattr(e, 'stderr') and e.stderr:
             # stderr might be bytes or str depending on the error and Python version
            stderr_str = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else e.stderr
            print(f"Stderr: {stderr_str}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Clean up intermediate files
        if not args.keep_intermediates:
            print("Cleaning up intermediate files...")
            for path in [sdr_path, hdr_path, hdr_raw_path]:
                if os.path.exists(path):
                    os.remove(path)
                    print(f"Removed {path}")


if __name__ == "__main__":
    main()