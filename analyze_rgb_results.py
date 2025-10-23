#!/usr/bin/env python3
"""
Analyze RGB (no conversion) test results.

Test results from hardware:
黄色 ↔ 緑 (inverted)
赤 ↔ 青 (inverted)
全体的に色が薄い (washed out/low saturation)
"""

def analyze_inversion():
    print("\n" + "="*80)
    print("RGB変換なしのテスト結果分析")
    print("="*80)

    # Original test (with BGR conversion)
    bgr_results = [
        ("赤", (255, 0, 0), (0, 0, 255), "赤", True),
        ("青", (0, 0, 255), (255, 0, 0), "白", False),
        ("緑", (0, 128, 0), (0, 128, 0), "黄色", False),
        ("黄色", (255, 255, 0), (0, 255, 255), "黄色", True),
    ]

    # New test (RGB, no conversion)
    rgb_results = [
        ("赤", (255, 0, 0), (255, 0, 0), "青", False),  # 逆
        ("青", (0, 0, 255), (0, 0, 255), "赤", False),  # 逆
        ("緑", (0, 128, 0), (0, 128, 0), "黄色", False),  # 逆
        ("黄色", (255, 255, 0), (255, 255, 0), "緑", False),  # 逆
    ]

    print("\n比較:")
    print("-" * 80)
    print(f"{'色名':<10} {'RGB入力':<20} {'BGR変換時の表示':<15} {'RGB直接の表示'}")
    print("-" * 80)

    for i in range(4):
        bgr_name, bgr_rgb, _, bgr_display, _ = bgr_results[i]
        rgb_name, rgb_rgb, _, rgb_display, _ = rgb_results[i]
        print(f"{bgr_name:<10} {str(bgr_rgb):<20} {bgr_display:<15} {rgb_display}")

    print("\n" + "="*80)
    print("パターンの発見")
    print("="*80)

    print("\n1. 色の反転パターン:")
    print("   赤 ↔ 青 (Red and Blue are swapped)")
    print("   黄色 ↔ 緑 (Yellow and Green are swapped)")

    print("\n2. これは完全な色反転（ネガティブ）ではない")
    print("   完全な色反転なら:")
    print("     赤(255,0,0) → シアン(0,255,255)")
    print("   しかし実際は:")
    print("     赤(255,0,0) → 青(0,0,255)")

    print("\n3. これはRとBチャンネルの入れ替えパターン!")
    print("   赤 RGB(255,0,0) → 青になる = RとBが逆")
    print("   青 RGB(0,0,255) → 赤になる = RとBが逆")
    print("   緑 RGB(0,128,0) → 黄色になる = ?")
    print("   黄色 RGB(255,255,0) → 緑になる = ?")

    print("\n" + "="*80)
    print("理論的分析")
    print("="*80)

    print("\nもしハードウェアがRとBチャンネルを逆に読んでいる場合:")
    print("-" * 80)
    print(f"{'入力RGB':<20} {'ハードウェアが読む':<20} {'期待される表示'}")
    print("-" * 80)

    test_cases = [
        ((255, 0, 0), (0, 0, 255), "青"),
        ((0, 0, 255), (255, 0, 0), "赤"),
        ((0, 128, 0), (0, 128, 0), "緑（変わらない）"),
        ((255, 255, 0), (0, 255, 255), "シアン"),
    ]

    for input_rgb, hw_reads, expected in test_cases:
        print(f"{str(input_rgb):<20} {str(hw_reads):<20} {expected}")

    print("\nしかし実際の結果:")
    print("  緑(0,128,0) → 黄色に表示される（緑ではない）")
    print("  黄色(255,255,0) → 緑に表示される（シアンではない）")

    print("\n矛盾がある！単純なRB入れ替えでは説明できない")

    print("\n" + "="*80)
    print("新しい仮説: RGB → BGR + 色反転")
    print("="*80)

    print("\nもしハードウェアが BGR + 補色変換 を行っている場合:")
    print("-" * 80)
    print(f"{'入力RGB':<20} {'BGR変換':<20} {'補色':<20} {'表示'}")
    print("-" * 80)

    # Test BGR + complement
    advanced_cases = [
        ("赤", (255, 0, 0), (0, 0, 255), (0, 255, 0), "緑?"),
        ("青", (0, 0, 255), (255, 0, 0), (0, 255, 255), "シアン?"),
        ("緑", (0, 128, 0), (0, 128, 0), (255, 127, 255), "?"),
        ("黄色", (255, 255, 0), (0, 255, 255), (255, 0, 0), "赤?"),
    ]

    for name, rgb, bgr, complement, expected in advanced_cases:
        print(f"{name:<10} {str(rgb):<20} {str(bgr):<20} {str(complement):<20} {expected}")

    print("\nこれも実際の結果と一致しない...")

    print("\n" + "="*80)
    print("実用的アプローチ: すべての順序をテスト")
    print("="*80)

    print("\n6つのチャンネル順序の結果を予測:")
    print("-" * 80)
    print(f"{'順序':<15} {'赤(255,0,0)':<20} {'青(0,0,255)':<20} {'判定'}")
    print("-" * 80)

    permutations = [
        ("RGB", (255, 0, 0), (0, 0, 255), "赤→青, 青→赤 (現在の結果)"),
        ("RBG", (255, 0, 0), (0, 255, 0), "?"),
        ("GRB", (0, 255, 0), (0, 0, 255), "?"),
        ("GBR", (0, 0, 255), (255, 0, 0), "これかも！赤→青→赤になる"),
        ("BRG", (0, 255, 0), (255, 0, 0), "?"),
        ("BGR", (0, 0, 255), (255, 0, 0), "赤→赤, 青→白 (前回の結果)"),
    ]

    for perm_name, red_result, blue_result, note in permutations:
        print(f"{perm_name:<15} {str(red_result):<20} {str(blue_result):<20} {note}")

    print("\n" + "="*80)
    print("「色が薄い」問題")
    print("="*80)

    print("\n色が薄く見える原因:")
    print("  1. コントラストが低い")
    print("  2. 彩度が低い")
    print("  3. Floyd-Steinbergディザリングで色が混ざる")
    print("  4. ハードウェアのインク濃度の問題")

    print("\n解決策:")
    print("  1. ImageEnhance.Color で彩度を上げる")
    print("  2. ImageEnhance.Contrast でコントラストを上げる")
    print("  3. しかし以前これらを削除したのは複雑すぎたから...")

    print("\n" + "="*80)
    print("次のアクション")
    print("="*80)

    print("""
最優先: 正しいチャンネル順序を見つける

方法1: 既存の順序テスト画像を使用
  /tmp/test_permutation_GBR.jpg をテスト
  これが最も可能性が高い

方法2: 全6つの順序をテスト
  すべての順序画像で最も正しく見える順序を選ぶ

その後、色が薄い問題に対処:
  - 適度な彩度/コントラスト強化を追加
  - 過度にならないように注意
    """)

def create_gbr_test():
    """Create GBR test to verify hypothesis"""
    from PIL import Image, ImageDraw

    print("\n" + "="*80)
    print("GBR順序のテスト画像を作成")
    print("="*80)

    colors = [
        ("red", (255, 0, 0)),
        ("blue", (0, 0, 255)),
        ("green", (0, 128, 0)),
        ("yellow", (255, 255, 0)),
    ]

    print("\nGBR変換を適用したテスト画像:")
    for name, (r, g, b) in colors:
        # Apply GBR transformation
        gbr_color = (g, b, r)

        img = Image.new('RGB', (800, 480), color=gbr_color)
        draw = ImageDraw.Draw(img)

        text_color = (255, 255, 255) if sum(gbr_color) < 384 else (0, 0, 0)
        draw.text((50, 50), f"{name.upper()}\nOriginal RGB{(r,g,b)}\nGBR{gbr_color}", fill=text_color)

        filename = f"/tmp/test_{name}_gbr.jpg"
        img.save(filename, quality=100)

        print(f"  ✓ {name:<10} RGB{(r,g,b)} → GBR{gbr_color} → {filename}")

    print("\nこれらをテストして、すべての色が正しく表示されるか確認してください")

def main():
    analyze_inversion()
    create_gbr_test()

    print("\n" + "="*80)
    print("推奨される次のステップ")
    print("="*80)
    print("""
1. まず GBR順序をテスト（最も可能性が高い）:
   python3 display/display_manager.py display /tmp/test_red_gbr.jpg
   → 赤が表示されるか？

2. もしGBRが正しい場合:
   display_manager.py を更新:
     r, g, b = optimized_image.split()
     display_image = Image.merge('RGB', (g, b, r))  # GBR order

3. すべての色をテスト

4. 色が薄い問題を解決:
   適度な彩度/コントラスト強化を追加
    """)

if __name__ == '__main__':
    main()
