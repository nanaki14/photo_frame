#!/usr/bin/env python3
"""
Analyze the test results to identify the correct color mapping.

Test results from hardware:
赤 (255,0,0) → BGR(0,0,255) → 赤 ✓
青 (0,0,255) → BGR(255,0,0) → 白 ✗
緑 (0,128,0) → BGR(0,128,0) → 黄色 ✗
黄色 (255,255,0) → BGR(0,255,255) → 黄色 ✓
"""

def analyze_results():
    print("\n" + "="*80)
    print("テスト結果の分析")
    print("="*80)

    # Test results
    results = [
        ("赤", (255, 0, 0), (0, 0, 255), "赤", True),
        ("青", (0, 0, 255), (255, 0, 0), "白", False),
        ("緑", (0, 128, 0), (0, 128, 0), "黄色", False),
        ("黄色", (255, 255, 0), (0, 255, 255), "黄色", True),
    ]

    print("\n現在の変換（BGR）:")
    print("-" * 80)
    print(f"{'色名':<10} {'RGB入力':<20} {'BGR変換後':<20} {'表示結果':<10} {'正否'}")
    print("-" * 80)

    for name, rgb, bgr, display, correct in results:
        status = "✓" if correct else "✗"
        print(f"{name:<10} {str(rgb):<20} {str(bgr):<20} {display:<10} {status}")

    print("\n" + "="*80)
    print("パターン分析")
    print("="*80)

    # Waveshare 6-color palette
    spectra_palette = {
        "Black": (0, 0, 0),
        "White": (255, 255, 255),
        "Red": (255, 0, 0),
        "Yellow": (255, 255, 0),
        "Green": (0, 128, 0),
        "Blue": (0, 0, 255),
    }

    print("\nWaveshare Spectra 6カラーパレット:")
    for name, rgb in spectra_palette.items():
        print(f"  {name:<10} RGB{rgb}")

    print("\n" + "="*80)
    print("重要な発見")
    print("="*80)

    print("\n1. 赤 (255,0,0) → BGR(0,0,255) → 赤に表示 ✓")
    print("   これは正しく動作しています")
    print("   Waveshareは BGR(0,0,255) を「赤」として認識")

    print("\n2. 青 (0,0,255) → BGR(255,0,0) → 白に表示 ✗")
    print("   これは予期しない結果です")
    print("   BGR(255,0,0) が「白」として表示される")
    print("   期待: BGR(255,0,0) = Waveshare Red")
    print("   実際: BGR(255,0,0) = White (?)")

    print("\n3. 緑 (0,128,0) → BGR(0,128,0) → 黄色に表示 ✗")
    print("   緑がそのまま渡されているが黄色になる")
    print("   BGR変換の影響なし（Gチャンネルは変わらない）")

    print("\n4. 黄色 (255,255,0) → BGR(0,255,255) → 黄色に表示 ✓")
    print("   これは正しく動作しています")
    print("   BGR(0,255,255) を「黄色」として認識")

    print("\n" + "="*80)
    print("仮説: RGBのままが正しい？")
    print("="*80)

    print("\nBGR変換を削除した場合:")
    print("-" * 80)
    print(f"{'色名':<10} {'RGB入力':<20} {'変換なし':<20} {'期待される表示'}")
    print("-" * 80)

    # Test without BGR conversion
    no_conversion = [
        ("赤", (255, 0, 0), (255, 0, 0), "?"),
        ("青", (0, 0, 255), (0, 0, 255), "?"),
        ("緑", (0, 128, 0), (0, 128, 0), "?"),
        ("黄色", (255, 255, 0), (255, 255, 0), "?"),
    ]

    for name, rgb, output, expected in no_conversion:
        print(f"{name:<10} {str(rgb):<20} {str(output):<20} {expected}")

    print("\n結論: RGBのままテストする必要があります")

    print("\n" + "="*80)
    print("奇妙な点")
    print("="*80)

    print("\nBGR(255,0,0) が2つの異なる結果を生成:")
    print("  青のテスト: BGR(255,0,0) → 白に表示")
    print("  （以前）   : BGR(255,0,0) → 黄色っぽく表示")
    print("\nこれは:")
    print("  1. Waveshare getbuffer()が画像全体を見て判断している")
    print("  2. 単色画像で特別な処理をしている")
    print("  3. Floyd-Steinbergディザリングの影響")

    print("\n" + "="*80)
    print("次のステップ")
    print("="*80)

    print("\n1. BGR変換を削除してRGBのままテスト")
    print("   - display_manager.py のBGR変換コードをコメントアウト")
    print("   - 同じ4つの画像で再テスト")

    print("\n2. RGBテストの結果:")
    print("   予測: すべての色が正しく表示される可能性が高い")

    print("\n3. もしRGBでも正しくない場合:")
    print("   - 他の順序（RBG, GRB, GBR, BRG）をテスト")
    print("   - Waveshare公式サンプルコードを確認")

def create_rgb_test_images():
    """Create test images WITHOUT BGR conversion for comparison"""
    from PIL import Image, ImageDraw

    print("\n" + "="*80)
    print("RGB変換なしのテスト画像を作成")
    print("="*80)

    colors = [
        ("red_rgb", (255, 0, 0)),
        ("blue_rgb", (0, 0, 255)),
        ("green_rgb", (0, 128, 0)),
        ("yellow_rgb", (255, 255, 0)),
    ]

    print("\n次のステップで使用するテスト画像:")
    for name, color in colors:
        img = Image.new('RGB', (800, 480), color=color)
        draw = ImageDraw.Draw(img)

        text_color = (255, 255, 255) if sum(color) < 384 else (0, 0, 0)
        draw.text((50, 50), f"{name.upper()}\nRGB{color}\nNO CONVERSION", fill=text_color)

        filename = f"/tmp/test_{name}_no_conversion.jpg"
        img.save(filename, quality=100)

        print(f"  ✓ {filename}")

    print("\nこれらの画像は、コード修正後にテストします")

def main():
    analyze_results()
    create_rgb_test_images()

    print("\n" + "="*80)
    print("アクションプラン")
    print("="*80)
    print("""
現在のテスト結果から、BGR変換が正しく機能していないことが明確です。

次のアクション:
1. display_manager.py のBGR変換を削除（RGB のまま使用）
2. サービスを再起動
3. 同じ4つの画像で再テスト:
   - test_simple_red.jpg
   - test_simple_blue.jpg
   - test_simple_green.jpg
   - test_simple_yellow.jpg

期待される結果:
- すべての色が正しく表示される
- または、新しいパターンが見つかる

このテストで最終的な答えが得られるはずです。
    """)

if __name__ == '__main__':
    main()
