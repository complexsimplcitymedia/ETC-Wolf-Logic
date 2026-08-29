#!/usr/bin/env python3
"""
Wolf Logic — Eos Magic Sheet High-Res Black Background PNG Generator
Creates a crisp 1920x1080 (16:9) solid deep black background PNG with professional
theatrical architectural outlines ready to import directly into ETC Eos Magic Sheets.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_magic_sheet_png(output_path, width=1920, height=1080):
    # Pure deep black background (#000000)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Color Palette
    CYAN = (0, 229, 255, 255)
    CYAN_DIM = (0, 229, 255, 70)
    BLUE_WALL = (30, 58, 138, 255)
    BLUE_BORDER = (96, 165, 250, 255)
    AMBER = (255, 145, 0, 255)
    MAGENTA = (217, 70, 239, 255)
    GRID_BORDER = (59, 130, 246, 180)
    WHITE_DIM = (255, 255, 255, 120)
    WHITE_FAINT = (255, 255, 255, 30)

    # Border frame around the entire stage area
    draw.rectangle([(40, 40), (width - 40, height - 40)], outline=CYAN_DIM, width=2)

    # Header Title
    draw.text((60, 60), "WOLF LOGIC — STAGE VENUE ARCHITECTURE", fill=CYAN)
    draw.text((width - 320, 60), "ETC EOS MAGIC SHEET TEMPLATE", fill=WHITE_DIM)

    # 1. UPSTAGE LED VIDEO WALL
    # Center X: width / 2 = 960
    wall_w = 900
    wall_h = 60
    wall_x0 = (width - wall_w) // 2
    wall_y0 = 120
    draw.rectangle([(wall_x0, wall_y0), (wall_x0 + wall_w, wall_y0 + wall_h)], 
                   fill=BLUE_WALL, outline=BLUE_BORDER, width=3)
    draw.text((wall_x0 + 320, wall_y0 + 20), "UPSTAGE LED VIDEO WALL", fill=(255, 255, 255, 255))

    # 2. MIDSTAGE ELECTRIC PIPE (TRUSS)
    truss_y = 240
    truss_x0 = 420
    truss_x1 = 1500
    # Dashed line representation
    for x in range(truss_x0, truss_x1, 30):
        draw.line([(x, truss_y), (x + 18, truss_y)], fill=WHITE_DIM, width=3)
    draw.text(((truss_x0 + truss_x1) // 2 - 140, truss_y - 28), "MIDSTAGE ELECTRIC (CH 101-110)", fill=WHITE_DIM)

    # Fixture hanging points (Circles for Channel 101 - 110)
    step = (truss_x1 - truss_x0) // 10
    for i in range(10):
        fx = truss_x0 + (i * step) + (step // 2)
        draw.ellipse([(fx - 18, truss_y - 18), (fx + 18, truss_y + 18)], outline=CYAN, width=2)
        draw.text((fx - 12, truss_y - 8), f"{101+i}", fill=CYAN)

    # 3. STAGE LEFT & STAGE RIGHT LED COLUMNS
    col_w = 50
    col_h = 130
    # Stage Left Column (Audience Right)
    col_sl_x = 320
    col_y0 = 290
    draw.rectangle([(col_sl_x, col_y0), (col_sl_x + col_w, col_y0 + col_h)], outline=(129, 140, 248, 255), width=2)
    draw.text((col_sl_x + 8, col_y0 + 50), "LED", fill=(199, 210, 254, 255))

    # Stage Right Column (Audience Left)
    col_sr_x = 1550
    draw.rectangle([(col_sr_x, col_y0), (col_sr_x + col_w, col_y0 + col_h)], outline=(129, 140, 248, 255), width=2)
    draw.text((col_sr_x + 8, col_y0 + 50), "LED", fill=(199, 210, 254, 255))

    # STAGE CENTER WATERMARK
    draw.text((width // 2 - 120, 320), "S T A G E", fill=WHITE_FAINT)

    # Centerline Specials (501 - 503)
    for idx, cy in enumerate([290, 350, 410]):
        cx = width // 2
        draw.ellipse([(cx - 16, cy - 16), (cx + 16, cy + 16)], outline=MAGENTA, width=2)
        draw.text((cx - 12, cy - 7), f"{501+idx}", fill=MAGENTA)

    # 4. PROSCENIUM FRONT WASH
    pros_y = 480
    pros_x0 = 360
    pros_x1 = 1560
    draw.line([(pros_x0, pros_y), (pros_x1, pros_y)], fill=(255, 255, 255, 200), width=4)
    draw.text((width // 2 - 160, pros_y - 25), "PROSCENIUM FRONT WASH (CH 201-208)", fill=AMBER)

    wash_step = (pros_x1 - pros_x0) // 8
    for i in range(8):
        wx = pros_x0 + (i * wash_step) + (wash_step // 2)
        draw.ellipse([(wx - 18, pros_y - 18), (wx + 18, pros_y + 18)], outline=AMBER, width=2)
        draw.text((wx - 12, pros_y - 8), f"{201+i}", fill=AMBER)

    # 5. AUDIENCE SEATING — OVERHEAD GLOWING LED LINEAR STRIPS (GRID)
    aud_w = 900
    aud_h = 340
    aud_x0 = (width - aud_w) // 2
    aud_y0 = 550
    draw.rectangle([(aud_x0, aud_y0), (aud_x0 + aud_w, aud_y0 + aud_h)], outline=CYAN_DIM, width=2)
    draw.text((width // 2 - 200, aud_y0 + 160), "OVERHEAD LED LINEAR STRIPS & SEATING", fill=WHITE_FAINT)

    # 4 Vertical LED Linear Strip Lines
    vert_cols = [aud_x0 + int(aud_w * 0.15), aud_x0 + int(aud_w * 0.38), 
                 aud_x0 + int(aud_w * 0.62), aud_x0 + int(aud_w * 0.85)]
    for vx in vert_cols:
        draw.line([(vx, aud_y0), (vx, aud_y0 + aud_h)], fill=(0, 229, 255, 100), width=3)

    # 5 Horizontal Overhead Glowing LED Linear Strips (Alternating Cyan & Magenta)
    strip_colors = [
        (0, 229, 255, 255),    # 1. Cyan
        (255, 0, 127, 255),    # 2. Magenta
        (0, 229, 255, 255),    # 3. Cyan
        (255, 0, 127, 255),    # 4. Magenta
        (0, 229, 255, 255),    # 5. Cyan
    ]
    h_step = aud_h // 4
    for s_idx, scolor in enumerate(strip_colors):
        sy = aud_y0 + (s_idx * (aud_h // 5)) + 30
        if s_idx == 4:
            sy = aud_y0 + aud_h - 20
        # Draw thick glowing linear LED strip
        draw.line([(aud_x0 + 10, sy), (aud_x0 + aud_w - 10, sy)], fill=scolor, width=6)

    # FOH Overhead Moving Head Spot Nodes at Grid Intersections (Ch 401 - 416)
    mover_rows = [aud_y0 + 30, aud_y0 + 100, aud_y0 + 170, aud_y0 + 240]
    RED_MOVER = (255, 23, 68, 255)
    for r_idx, my in enumerate(mover_rows):
        for c_idx, mx in enumerate(vert_cols):
            ch_num = 401 + (r_idx * 4) + c_idx
            # Red moving head circle with white border
            draw.ellipse([(mx - 15, my - 15), (mx + 15, my + 15)], fill=RED_MOVER, outline=(255, 255, 255, 255), width=2)
            draw.text((mx - 11, my - 7), f"{ch_num}", fill=(255, 255, 255, 255))

    # Centerline Specials (Ch 501, 502, 503)
    center_x = width // 2
    for s_idx, spy in enumerate([aud_y0 + 30, aud_y0 + 170, aud_y0 + aud_h - 20]):
        draw.ellipse([(center_x - 15, spy - 15), (center_x + 15, spy + 15)], fill=(255, 214, 0, 255), outline=(255, 255, 255, 255), width=2)
        draw.text((center_x - 11, spy - 7), f"{501+s_idx}", fill=(0, 0, 0, 255))

    # 6. FOH MIX & LIGHTING CONTROL STATION
    foh_w = 400
    foh_h = 50
    foh_x0 = (width - foh_w) // 2
    foh_y0 = 940
    draw.rectangle([(foh_x0, foh_y0), (foh_x0 + foh_w, foh_y0 + foh_h)], 
                   fill=(14, 23, 38, 255), outline=CYAN, width=2)
    draw.text((foh_x0 + 35, foh_y0 + 15), "FOH MIX & LIGHTING CONTROL (EOS / iPAD)", fill=CYAN)

    # Save to disk
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"✓ Magic Sheet 1080p Black Background PNG saved to: {output_path}")

if __name__ == "__main__":
    out_file = "/mnt/wolf-thumb/ETC-Wolf/public/magic_sheet_black_bg.png"
    create_magic_sheet_png(out_file)
