#!/usr/bin/env python3
"""
濃い青が赤になる問題のデバッグスクリプト

実行方法:
1. Raspberry Piで実際の濃い青画像をアップロード
2. このスクリプトを実行して問題を診断
"""

import sys
import os
from PIL import Image, ImageDraw, ImageEnhance
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'display'))

# 色定義
CORE_COLORS = [
    (0, 0, 0),          # Black
    (255, 255, 255),    # White
    (255, 0, 0),        # Red
    (255, 255, 0),      # Yellow
    (0, 128, 0),        # Green
    (0, 0, 255),        # Blue
]

COLOR_NAMES = ["Black", "White", "Red", "Yellow", "Green", "Blue"]

def euclidean_distance(r1, g1, b1, r2, g2, b2):
    return math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)

def find_closest_color(r, g, b):
    min_distance = float('inf')
    closest_idx = 0
    distances = []

    for idx, (cr, cg, cb) in enumerate(CORE_COLORS):
        distance = euclidean_distance(r, g, b, cr, cg, cb)
        distances.append((idx, distance))
        if distance < min_distance:
            min_distance = distance
            closest_idx = idx

    return closest_idx, sorted(distances, key=lambda x: x[1])

def analyze_pixel_color(r, g, b, label=""):
    """1つのピクセルを詳しく分析"""
    closest_idx, distances = find_closest_color(r, g, b)

    print(f"\n{label}")
    print(f"  元の色: RGB({r}, {g}, {b})")
    print(f"  マップ先: {COLOR_NAMES[closest_idx]} {CORE_COLORS[closest_idx]}")
    print(f"\n  全パレット距離:")
    for idx, dist in distances:
        print(f"    {COLOR_NAMES[idx]:8} {str(CORE_COLORS[idx]):15} distance={dist:7.1f}")

    return closest_idx

def analyze_image_colors(image_path, num_samples=10):
    """画像からサンプルピクセルを取得して分析"""

    if not os.path.exists(image_path):
        print(f"❌ ファイルが見つかりません: {image_path}")
        return

    img = Image.open(image_path)
    print(f"\n画像: {image_path}")
    print(f"サイズ: {img.size}")
    print(f"モード: {img.mode}")

    # ランダムサンプル取得
    width, height = img.size
    step_x = max(1, width // (int(num_samples**0.5)))
    step_y = max(1, height // (int(num_samples**0.5)))

    dark_blues_found = []
    dark_reds_found = []

    for y in range(0, height, step_y):
        for x in range(0, width, step_x):
            pixel = img.getpixel((x, y))

            # RGB値の取得
            if isinstance(pixel, tuple):
                r, g, b = pixel[:3]
            else:
                r = g = b = pixel

            # 濃い青の判定: B > R, B > G, かつ濃い
            if b > 100 and b > r and b > g and sum((r, g, b)) < 400:
                dark_blues_found.append((x, y, r, g, b))

            # 濃い赤の判定: R > G, R > B, かつ濃い
            if r > 100 and r > g and r > b and sum((r, g, b)) < 400:
                dark_reds_found.append((x, y, r, g, b))

    print(f"\n発見された濃い青: {len(dark_blues_found)}")
    for x, y, r, g, b in dark_blues_found[:5]:  # 最初の5つを表示
        analyze_pixel_color(r, g, b, f"  位置({x}, {y})")

    print(f"\n発見された濃い赤: {len(dark_reds_found)}")
    for x, y, r, g, b in dark_reds_found[:5]:
        analyze_pixel_color(r, g, b, f"  位置({x}, {y})")

def create_test_image_with_dark_colors():
    """テスト画像を作成"""
    img = Image.new('RGB', (800, 480), color='white')
    draw = ImageDraw.Draw(img)

    # テスト色
    test_colors = [
        ("Pure Dark Blue", (0, 0, 128), 0, 0),
        ("Navy/Purple", (25, 40, 80), 200, 0),
        ("Dark Sky Blue", (30, 60, 140), 400, 0),
        ("Clothing Dark Blue", (40, 70, 150), 600, 0),
        ("Pure Red", (255, 0, 0), 0, 120),
        ("Dark Red", (128, 0, 0), 200, 120),
        ("Very Dark Red", (80, 20, 20), 400, 120),
    ]

    for label, color, x, y in test_colors:
        draw.rectangle([x, y, x + 150, y + 100], fill=color)
        draw.text((x, y + 105), label, fill=(0, 0, 0))

    test_path = '/tmp/debug_dark_colors.png'
    img.save(test_path)
    print(f"\n✓ テスト画像作成: {test_path}")

    return test_path

def main():
    print("=" * 80)
    print("濃い青→濃い赤 マッピング問題デバッグツール")
    print("=" * 80)

    # テスト画像作成
    test_image = create_test_image_with_dark_colors()

    # テスト画像を処理
    print("\n【テスト画像の処理】")
    from PIL import Image as PILImage, ImageEnhance

    img = PILImage.open(test_image)

    # 強化パイプライン適用
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.5)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.1)

    enhanced_path = '/tmp/debug_dark_colors_enhanced.png'
    img.save(enhanced_path)
    print(f"✓ 強化後の画像: {enhanced_path}")

    # 実際のアップロード画像があればそれも分析
    upload_dir = os.path.expanduser('~/uploads')
    if os.path.exists(upload_dir):
        files = [f for f in os.listdir(upload_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        if files:
            print(f"\n【アップロード画像の分析】")
            for file in files[:1]:  # 最初の1つを分析
                filepath = os.path.join(upload_dir, file)
                analyze_image_colors(filepath, num_samples=10)

    # 診断画像が存在すれば分析
    diagnostic_images = [
        '/tmp/02_after_saturation.png',
        '/tmp/03_after_contrast.png',
        '/tmp/05_after_dithering.png',
        '/tmp/06_final_6color_mapped.png',
    ]

    print(f"\n【診断画像の分析】")
    for diag_path in diagnostic_images:
        if os.path.exists(diag_path):
            analyze_image_colors(diag_path, num_samples=5)

    print("\n" + "=" * 80)
    print("デバッグ完了")
    print("=" * 80)
    print("\n提案:")
    print("1. 実際の濃い青画像をアップロード")
    print("2. このスクリプトを実行: python3 debug_dark_blue.py")
    print("3. 出力から、どの処理ステップで色が変わるか確認")
    print("4. 問題が見つかったら、その処理を修正")

if __name__ == '__main__':
    main()
