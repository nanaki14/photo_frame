#!/usr/bin/env python3
"""
Analyze GBR test results and determine the correct permutation.

Test results from hardware (GBR):
赤 → 赤 ✓
青 → 黄色 ✗ (should be blue)
緑 → 緑 ✓
黄色 → 青 ✗ (should be yellow)
"""

def analyze_all_tests():
    print("\n" + "="*80)
    print("全テスト結果の比較")
    print("="*80)

    # All test results
    all_results = {
        "BGR": {
            "赤": "赤 ✓",
            "青": "白 ✗",
            "緑": "黄色 ✗",
            "黄色": "黄色 ✓",
        },
        "RGB": {
            "赤": "青 ✗",
            "青": "赤 ✗",
            "緑": "黄色 ✗",
            "黄色": "緑 ✗",
        },
        "GBR": {
            "赤": "赤 ✓",
            "青": "黄色 ✗",
            "緑": "緑 ✓",
            "黄色": "青 ✗",
        },
    }

    print("\n" + "-" * 80)
    print(f"{'色':<10} {'BGR':<15} {'RGB':<15} {'GBR':<15}")
    print("-" * 80)
    for color in ["赤", "青", "緑", "黄色"]:
        print(f"{color:<10} {all_results['BGR'][color]:<15} {all_results['RGB'][color]:<15} {all_results['GBR'][color]:<15}")

    print("\n" + "="*80)
    print("パターン分析")
    print("="*80)

    print("\nGBRの結果:")
    print("  赤 → 赤 ✓")
    print("  緑 → 緑 ✓")
    print("  青 ↔ 黄色 ✗ (入れ替わっている)")

    print("\n青と黄色の成分:")
    print("  青:   RGB(0,   0,   255)")
    print("  黄色: RGB(255, 255, 0)")

    print("\nGBR変換後:")
    print("  青:   RGB(0,   0,   255) → GBR(0,   255, 0)")
    print("  黄色: RGB(255, 255, 0)   → GBR(255, 0,   255)")

    print("\nもしハードウェアがGBR順序で読むなら:")
    print("  青のGBR(0, 255, 0):     G=0,   B=255, R=0   → 青になるはず")
    print("  黄色のGBR(255, 0, 255): G=255, B=0,   R=255 → 黄色になるはず")
    print("\nしかし実際は逆！これはGBRが正しくないことを示す")

    print("\n" + "="*80)
    print("残りの順序を分析")
    print("="*80)

    print("\nテストしていない順序: RBG, GRB, BRG")

    # Analyze each permutation
    test_colors = [
        ("赤", (255, 0, 0)),
        ("青", (0, 0, 255)),
        ("緑", (0, 128, 0)),
        ("黄色", (255, 255, 0)),
    ]

    permutations = [
        ("RBG", lambda r, g, b: (r, b, g)),
        ("GRB", lambda r, g, b: (g, r, b)),
        ("BRG", lambda r, g, b: (b, r, g)),
    ]

    for perm_name, perm_func in permutations:
        print(f"\n{perm_name}変換の予測:")
        print("-" * 70)
        for color_name, (r, g, b) in test_colors:
            result = perm_func(r, g, b)
            print(f"  {color_name:<10} RGB{(r,g,b)} → {perm_name}{result}")

    print("\n" + "="*80)
    print("RBG順序の詳細分析")
    print("="*80)

    print("\nRBG変換 = RとBは変えず、GとBを入れ替える")
    print("\n変換結果:")
    print("-" * 70)
    print(f"{'色':<10} {'RGB入力':<20} {'RBG変換後':<20} {'予測'}")
    print("-" * 70)

    rbg_predictions = [
        ("赤",   (255, 0, 0),   (255, 0, 0),   "赤のまま（RとGが0）"),
        ("青",   (0, 0, 255),   (0, 255, 0),   "緑？"),
        ("緑",   (0, 128, 0),   (0, 0, 128),   "暗い青？"),
        ("黄色", (255, 255, 0), (255, 0, 255), "マゼンタ？"),
    ]

    for name, rgb, rbg, note in rbg_predictions:
        print(f"{name:<10} {str(rgb):<20} {str(rbg):<20} {note}")

    print("\n" + "="*80)
    print("BRG順序の詳細分析")
    print("="*80)

    print("\nBRG変換:")
    print("-" * 70)
    print(f"{'色':<10} {'RGB入力':<20} {'BRG変換後':<20} {'予測'}")
    print("-" * 70)

    brg_predictions = [
        ("赤",   (255, 0, 0),   (0, 255, 0),   "緑？"),
        ("青",   (0, 0, 255),   (255, 0, 0),   "赤？"),
        ("緑",   (0, 128, 0),   (0, 0, 128),   "暗い青？"),
        ("黄色", (255, 255, 0), (0, 255, 255), "シアン？"),
    ]

    for name, rgb, brg, note in brg_predictions:
        print(f"{name:<10} {str(rgb):<20} {str(brg):<20} {note}")

    print("\n" + "="*80)
    print("GRB順序の詳細分析")
    print("="*80)

    print("\nGRB変換:")
    print("-" * 70)
    print(f"{'色':<10} {'RGB入力':<20} {'GRB変換後':<20} {'予測'}")
    print("-" * 70)

    grb_predictions = [
        ("赤",   (255, 0, 0),   (0, 255, 0),   "緑？"),
        ("青",   (0, 0, 255),   (0, 0, 255),   "青のまま？"),
        ("緑",   (0, 128, 0),   (128, 0, 0),   "赤っぽい？"),
        ("黄色", (255, 255, 0), (255, 255, 0), "黄色のまま？"),
    ]

    for name, rgb, grb, note in grb_predictions:
        print(f"{name:<10} {str(rgb):<20} {str(grb):<20} {note}")

    print("\n" + "="*80)
    print("既知の結果から逆算")
    print("="*80)

    print("\n現在判明している正しいマッピング:")
    print("  赤 RGB(255,0,0)   → GBR(0,0,255)   → 赤 ✓ (正しい)")
    print("  緑 RGB(0,128,0)   → GBR(128,0,0)   → 緑 ✓ (正しい)")
    print("  青 RGB(0,0,255)   → GBR(0,255,0)   → 黄色 ✗")
    print("  黄色 RGB(255,255,0) → GBR(255,0,255) → 青 ✗")

    print("\n青と黄色だけが逆なので、GとBを修正すれば良い？")
    print("\n青を正しくするには:")
    print("  青 RGB(0,0,255) が 青になるには...")
    print("  現在: GBR(0,255,0) → 黄色になる")
    print("  必要: ???(?,?,?) → 青になる")

    print("\n黄色を正しくするには:")
    print("  黄色 RGB(255,255,0) が 黄色になるには...")
    print("  現在: GBR(255,0,255) → 青になる")
    print("  必要: ???(?,?,?) → 黄色になる")

    print("\n" + "="*80)
    print("新しい仮説: カスタムマッピングが必要？")
    print("="*80)

    print("\nもしかして、単純なチャンネル入れ替えでは解決できない？")
    print("ハードウェアが特定の色値を特別に処理している可能性")

    print("\nWaveshare Spectra 6の公式パレット:")
    palette = {
        "Black":  (0, 0, 0),
        "White":  (255, 255, 255),
        "Red":    (255, 0, 0),
        "Yellow": (255, 255, 0),
        "Green":  (0, 128, 0),  # 重要: 255ではなく128
        "Blue":   (0, 0, 255),
    }

    for name, rgb in palette.items():
        print(f"  {name:<10} RGB{rgb}")

    print("\n緑だけ (0, 128, 0) なのが重要！")

def create_remaining_permutation_tests():
    """Create test images for RBG, GRB, BRG"""
    from PIL import Image, ImageDraw

    print("\n" + "="*80)
    print("残りの順序テスト画像を作成")
    print("="*80)

    colors = [
        ("red", (255, 0, 0)),
        ("blue", (0, 0, 255)),
        ("green", (0, 128, 0)),
        ("yellow", (255, 255, 0)),
    ]

    permutations = [
        ("RBG", lambda r, g, b: (r, b, g)),
        ("GRB", lambda r, g, b: (g, r, b)),
        ("BRG", lambda r, g, b: (b, r, g)),
    ]

    for perm_name, perm_func in permutations:
        print(f"\n{perm_name}順序:")
        for color_name, (r, g, b) in colors:
            result = perm_func(r, g, b)

            img = Image.new('RGB', (800, 480), color=result)
            draw = ImageDraw.Draw(img)

            text_color = (255, 255, 255) if sum(result) < 384 else (0, 0, 0)
            draw.text((50, 50), f"{color_name.upper()}\nOriginal RGB{(r,g,b)}\n{perm_name}{result}", fill=text_color)

            filename = f"/tmp/test_{color_name}_{perm_name.lower()}.jpg"
            img.save(filename, quality=100)

            print(f"  ✓ {color_name:<10} RGB{(r,g,b)} → {perm_name}{result} → {filename}")

def main():
    analyze_all_tests()
    create_remaining_permutation_tests()

    print("\n" + "="*80)
    print("次のアクション")
    print("="*80)
    print("""
最も効率的なテスト方法:

オプション1: 既存の順序テスト画像を使用
  /tmp/test_permutation_RBG.jpg
  /tmp/test_permutation_GRB.jpg
  /tmp/test_permutation_BRG.jpg

オプション2: 個別テスト画像を使用
  /tmp/test_red_rbg.jpg など

推奨: オプション1（1枚の画像ですべての色を確認できる）

各画像をテストして、4色すべてが正しく表示される順序を見つけてください:
  赤 → 赤 ✓
  青 → 青 ✓
  緑 → 緑 ✓
  黄色 → 黄色 ✓

その順序が正解です！
    """)

if __name__ == '__main__':
    main()
