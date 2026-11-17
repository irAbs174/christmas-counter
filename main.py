# Matrix-style Christmas countdown

"""
Input (keep beside this script): happy_christmas_2027.png

Simple render:
  python3 create_christmas_countdown.py

Render with x Days left:
  python3 create_christmas_countdown.py --days 62

Render simple frame:
  python3 create_christmas_countdown.py --days 1 --no-video

Customize quality:
  python3 create_christmas_countdown.py --days 10 --duration 8 --fps 24
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import argparse, math, os, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(HERE, "happy_christmas_2027.png")
W, H = 1080, 1920
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
RED = (255, 56, 78)
BRIGHT_RED = (255, 94, 105)
WHITE = (255, 247, 247)


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def text_center(draw, text, box, font, fill, stroke_width=0, stroke_fill=(0, 0, 0)):
    x1, y1, x2, y2 = box
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = x1 + (x2 - x1 - tw) / 2 - bbox[0]
    y = y1 + (y2 - y1 - th) / 2 - bbox[1]
    draw.text((int(x), int(y)), text, font=font, fill=fill,
              stroke_width=stroke_width, stroke_fill=stroke_fill)


def flag_points(t):
    """Return a subtly waving rectangular red-flag polygon."""
    points = [(155, 1435)]
    for i in range(1, 9):
        x = 155 + i * 28
        y = 1435 + math.sin(t * 2.5 + i * 0.48) * (3 + i * 0.8)
        points.append((int(x), int(y)))
    for i in range(8, 0, -1):
        x = 155 + i * 28
        y = 1572 + math.sin(t * 2.5 + i * 0.48 + 1.1) * (3 + i * 0.8)
        points.append((int(x), int(y)))
    points.append((155, 1572))
    return points


def render_frame(base, label, t=0.0):
    img = base.convert("RGBA")
    pulse = 0.78 + 0.22 * (0.5 + 0.5 * math.sin(t * math.tau / 2.8))

    # Red neon halo around the countdown panel and the flag.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle((370, 1418, 920, 1590), radius=24,
                         outline=(255, 30, 58, int(220 * pulse)), width=12)
    gd.polygon(flag_points(t), fill=(255, 24, 44, int(95 * pulse)))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(22)))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Dark HUD plaque keeps the countdown readable over the binary rain.
    d.rounded_rectangle((370, 1420, 920, 1588), radius=22,
                        fill=(3, 8, 12, 222), outline=(255, 65, 83, int(235 * pulse)), width=4)
    d.rounded_rectangle((385, 1435, 905, 1573), radius=15,
                        outline=(255, 65, 83, int(105 * pulse)), width=2)
    # Small circuit-style brackets around the plaque.
    d.line((346, 1450, 370, 1450), fill=(255, 70, 89, 235), width=4)
    d.line((346, 1450, 346, 1476), fill=(255, 70, 89, 235), width=4)
    d.line((920, 1532, 944, 1532), fill=(255, 70, 89, 235), width=4)
    d.line((944, 1506, 944, 1532), fill=(255, 70, 89, 235), width=4)

    # Flag pole and metallic finial.
    d.line((150, 1395, 150, 1635), fill=(190, 217, 220, 255), width=8)
    d.line((150, 1395, 150, 1635), fill=(255, 255, 255, 255), width=3)
    d.ellipse((140, 1385, 160, 1405), fill=(255, 90, 105, 255), outline=(255, 225, 225, 255), width=2)

    # Red flag with a bright top edge and a darker lower fold.
    points = flag_points(t)
    d.polygon(points, fill=(190, 10, 35, 250), outline=(255, 72, 88, 255))
    d.line(points[:9], fill=(255, 170, 170, 255), width=4)
    fold = [(155, 1516)]
    for i in range(1, 9):
        x = 155 + i * 28
        y = 1516 + math.sin(t * 2.5 + i * 0.48 + 0.7) * (2 + i * 0.7)
        fold.append((int(x), int(y)))
    d.line(fold, fill=(110, 3, 24, 210), width=5)
    # Small white highlight stitching at the hoist.
    d.line((165, 1445, 165, 1560), fill=(255, 180, 185, 190), width=2)

    # Slight red reflection along the lower edge of the banner.
    d.line((410, 1600, 880, 1600), fill=(255, 40, 60, int(105 * pulse)), width=2)

    img = Image.alpha_composite(img, overlay)

    # The countdown itself is rendered separately for a soft red glow.
    text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(text_layer)
    countdown_font = get_font(FONT_MONO_BOLD, 48 if len(label) <= 12 else 40)
    text_center(td, label, (400, 1430, 890, 1575), countdown_font,
                (255, int(105 + 65 * pulse), int(115 + 70 * pulse), 255),
                stroke_width=1, stroke_fill=(90, 0, 10, 255))
    halo = text_layer.filter(ImageFilter.GaussianBlur(14))
    # Turn the text halo into red-tinted light.
    halo_tint = Image.new("RGBA", (W, H), (255, 25, 48, 0))
    halo_tint.putalpha(halo.getchannel("A"))
    img = Image.alpha_composite(img, halo_tint)
    img = Image.alpha_composite(img, text_layer)

    # A small red beacon dot adds the same tech-HUD character as the poster.
    beacon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beacon)
    bd.ellipse((895, 1450, 909, 1464), fill=(255, 70, 88, int(130 * pulse)))
    img = Image.alpha_composite(img, beacon.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(img).ellipse((898, 1453, 906, 1461), fill=(255, 95, 110, 245))
    return img.convert("RGB")


def main():
    parser = argparse.ArgumentParser(description="Create a Matrix-style Christmas countdown poster and video.")
    parser.add_argument("--days", default="N", help="Countdown value (e.g. 30); defaults to the N-day template")
    parser.add_argument("--no-video", action="store_true", help="Create only the PNG poster")
    parser.add_argument("--duration", type=float, default=6.0, help="Video duration in seconds (default 6)")
    parser.add_argument("--fps", type=int, default=12, help="Video frame rate (default 12)")
    args = parser.parse_args()

    if not os.path.exists(BASE_PATH):
        raise FileNotFoundError(f"Missing approved base poster: {BASE_PATH}")
    try:
        n = int(args.days)
        if n < 0:
            raise ValueError
        label = f"{n} DAY LEFT" if n == 1 else f"{n} DAYS LEFT"
        slug = str(n)
    except ValueError:
        label = "N DAYS LEFT"
        slug = "N"

    base = Image.open(BASE_PATH).convert("RGB")
    still = render_frame(base, label, 0)
    png_path = os.path.join(HERE, f"christmas_countdown_{slug}_days_left.png")
    mp4_path = os.path.join(HERE, f"christmas_countdown_{slug}_days_left.mp4")
    still.save(png_path, quality=95)
    print("Created:", png_path)
    if args.no_video:
        return

    if args.duration <= 0 or args.fps <= 0:
        raise ValueError("--duration and --fps must be positive values")
    frame_count = max(1, int(args.duration * args.fps))
    with tempfile.TemporaryDirectory(prefix="christmas_countdown_") as tmp:
        for i in range(frame_count):
            frame = render_frame(base, label, i / args.fps)
            frame.save(os.path.join(tmp, f"frame_{i:05d}.jpg"), quality=93, optimize=True)
            if i % max(1, args.fps) == 0:
                print(f"Rendering frame {i + 1}/{frame_count}")
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
               "-framerate", str(args.fps), "-i", os.path.join(tmp, "frame_%05d.jpg"),
               "-c:v", "libx264", "-preset", "medium", "-crf", "18",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", mp4_path]
        subprocess.run(cmd, check=True)
    print("Created:", mp4_path)

if __name__ == "__main__":
    main()
