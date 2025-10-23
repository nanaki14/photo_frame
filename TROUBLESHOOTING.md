# トラブルシューティング: 濃い青が赤黒く見える問題

## 報告された症状

1. **濃い青の部分がまだ赤黒く見える**
2. **明るい色（城に近い色）が淡い青になってしまった**

## 根本原因の仮説

### 仮説 1: パレット定義が誤っている
- Green = (0, 128, 0) が正しいのか確認が必要
- 他の色定義（Red, Yellow, Blue）も正確か確認が必要
- Waveshareの公式ライブラリでは BGR 形式を使用している可能性

### 仮説 2: 直接マッピングのアルゴリズムが不適切
- ユークリッド距離による最近接色検索が最適でない
- Floyd-Steinberg ディザリングを使う公式の方法が必要

### 仮説 3: 強化パイプラインが不適切
- 彩度 1.5x、コントラスト 1.3x の値が適切でない
- 画像の種類によって異なる処理が必要

## デバッグ手順

### ステップ1: 実際のアップロード画像のピクセル値を確認

```bash
python3 << 'PYSCRIPT'
from PIL import Image
import os

# アップロード画像を読み込み
img_path = os.path.expanduser('~/uploads/photo.jpg')
if os.path.exists(img_path):
    img = Image.open(img_path)

    # 赤黒く見えている部分のピクセル値を確認
    # 画像の異なる位置から複数サンプルを取得
    print("Sampling pixels from uploaded image:")
    for y in [img.height // 4, img.height // 2, 3 * img.height // 4]:
        for x in [img.width // 4, img.width // 2, 3 * img.width // 4]:
            try:
                pixel = img.getpixel((x, y))
                print(f"  ({x}, {y}): RGB{pixel}")
            except:
                pass
else:
    print(f"Image not found: {img_path}")
PYSCRIPT
```

### ステップ2: 処理の各ステップでの色変化を追跡

```bash
python3 << 'PYSCRIPT'
from PIL import Image
import os

# 診断画像の色分布を確認
stages = {
    '/tmp/02_after_saturation.png': '彩度強化後',
    '/tmp/03_after_contrast.png': 'コントラスト強化後',
    '/tmp/05_after_dithering.png': '6色マッピング後',
}

for path, label in stages.items():
    if os.path.exists(path):
        img = Image.open(path)

        # 複数の位置でピクセル値を確認
        print(f"\n{label} ({path}):")
        for y in [img.height // 4, img.height // 2, 3 * img.height // 4]:
            for x in [img.width // 4, img.width // 2, 3 * img.width // 4]:
                try:
                    pixel = img.getpixel((x, y))
                    print(f"  ({x}, {y}): RGB{pixel}")
                except:
                    pass
PYSCRIPT
```

### ステップ3: Waveshareの公式パレット定義を確認

Waveshareの公式ライブラリ（epd7in3f.py）の色定義を確認してください：

```python
# 公式の色定義を探す
grep -r "color" /path/to/waveshare/lib/epd7in3f.py
# または
grep -r "(0, 0, 0)" /path/to/waveshare/lib/
```

## 考えられる解決策

### オプション A: 公式の quantize() を使用

前に削除したコードに戻す：

```python
palette_image = Image.new('P', (1, 1))
palette = []
for color in [(0, 0, 0), (255, 255, 255), (255, 0, 0), (255, 255, 0), (0, 128, 0), (0, 0, 255)]:
    palette.extend(color)
while len(palette) < 768:
    palette.append(0)
palette_image.putpalette(palette)

quantized = image.quantize(palette=palette_image, dither=Image.FLOYDSTEINBERG)
final_image = quantized.convert('RGB')
```

利点:
- Waveshare 公式の方法と同じ
- Floyd-Steinberg ディザリングが自動適用
- より滑らかな色表現

欠点:
- 以前、色情報が失われるという問題があった

### オプション B: パレット定義を再確認

Waveshareの公式ライブラリで使用されている正確な色定義を確認し、修正する。

### オプション C: 強化パイプラインを調整

現在の設定（彩度 1.5x、コントラスト 1.3x）では不十分な可能性があります。

別の値を試す：
- 彩度: 2.0x（1.5x より強い）
- コントラスト: 1.5x（1.3x より強い）

## 推奨される次のステップ

1. 上記のデバッグスクリプトを実行して、実際のピクセル値を取得
2. そのピクセル値が各処理ステップでどう変化するかを確認
3. 最終的なマッピング結果が期待と異なる場合、原因を特定
4. Waveshareの公式パレット定義を確認

##参考情報

- 公式 Waveshare E-Ink 7.3 inch HAT (E) Spectra 6
- Floyd-Steinberg ディザリング: 誤差拡散アルゴリズムで限定色での表現を改善
- 色空間: RGB vs BGR（Waveshareは BGR 形式を使用する可能性）
