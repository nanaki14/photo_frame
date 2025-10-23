# シンプルアプローチ: 色味を弄らない設計

## 概要

すべての複雑な色処理を削除し、**Waveshareの公式getbuffer()メソッドに完全に任せる**設計に変更しました。

## 前のアプローチの問題

複雑な色処理パイプラインがありました：

```
アップロード画像
  ↓
サーバー(Sharp): modulate(), sharpen()で色処理
  ↓
display_manager.py: ImageEnhance で彩度・コントラスト・明るさ調整
  ↓
カスタム6色マッピング（Euclidean距離）
  ↓
Waveshare getbuffer()
  ↓
ディスプレイ表示
```

**問題:**
- 複数の処理層で色が歪む
- 濃い青が赤黒くなる
- 明るい色が淡い青になる
- 不可知な相互作用

## 新しいシンプルアプローチ

```
アップロード画像
  ↓
サーバー(Sharp): リサイズのみ（色処理なし）
  ↓
display_manager.py: 表示サイズに調整（色処理なし）
  ↓
Waveshare getbuffer(): 公式の色変換 + Floyd-Steinberg ディザリング
  ↓
ディスプレイ表示
```

**メリット:**
✓ 色の歪みなし
✓ 公式の方法を使用
✓ 保守性が高い
✓ より高速（処理が少ない）
✓ Waveshare品質保証

## 処理フロー

### 1. サーバー側（src/server/app.ts）

```typescript
// 最小限の処理：リサイズのみ
const processedBuffer = await sharpInstance
    .resize(TARGET_WIDTH, TARGET_HEIGHT, {
        fit: 'contain',
        background: { r: 255, g: 255, b: 255 },
        kernel: isPi ? 'nearest' : 'lanczos3',
    })
    .jpeg({
        quality: 100,
        progressive: false,
        optimiseScans: false,
    })
    .toBuffer();
```

**削除されたもの:**
- `.modulate()` - 彩度、明るさ、色相の調整
- `.sharpen()` - 鋭さの調整
- すべての色処理ロジック

### 2. ディスプレイ側（display/display_manager.py）

```python
def optimize_image_for_eink(self, image_path):
    """
    最小限の処理：リサイズと中央配置のみ
    色変換は Waveshare getbuffer() に完全に任せる
    """
    # 画像をロード
    img = Image.open(image_path)

    # 中央に配置（白背景）
    background = Image.new('RGB', (self.display_width, self.display_height), 'white')
    background.paste(img, ...)

    # リサイズ（必要な場合）
    if background.size != (DISPLAY_WIDTH, DISPLAY_HEIGHT):
        background = background.resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), Image.Resampling.LANCZOS)

    # 色処理なし！
    return background
```

**削除されたもの:**
- ImageEnhance.Color() - 彩度調整
- ImageEnhance.Contrast() - コントラスト調整
- ImageEnhance.Brightness() - 明るさ調整
- カスタム6色マッピングロジック
- Euclidean距離計算

### 3. ディスプレイ表示

```python
# optimize_image_for_eink() からのRGB画像をそのまま使用
optimized_image = self.optimize_image_for_eink(image_path)

# Waveshare公式メソッドに完全に任せる
buffer = self.epd.getbuffer(optimized_image)
self.epd.display(buffer)
```

## Waveshare getbuffer() が行うこと

Waveshare の公式実装は：

1. **色量子化**: フルカラーRGBを6色に削減
2. **Floyd-Steinberg ディザリング**: 誤差拡散で滑らかに表現
3. **パレットマッピング**: 最適な6色へのマッピング
4. **バッファ生成**: ハードウェア固有フォーマット

これはWaveshareのエンジニアが実装・テストし、ハードウェアに最適化されています。

## 期待される動作

### 削減される問題

✗ 濃い青が赤黒くなる  → ✓ 濃い青が青で表示
✗ 明るい色が淡い青     → ✓ 元の色に近く表示
✗ 肌が白抜けになる    → ✓ 自然な色で表示
✗ 色のアーティファクト → ✓ 滑らかなディザリング

### デメリット（ほぼなし）

- 色が「すべての色」の画像には限界がある（6色のみ）
  - ただしこれはハードウェアの制限で、処理では解決できない

## デプロイ手順

```bash
cd /Users/masa/git/photo_frame
git pull origin main

# Raspberry Pi で
cd ~/photo_frame
git pull origin main
sudo systemctl restart photo-frame
```

## テスト

```bash
# Raspberry Pi で
python3 test_color_fix.py

# または実際の画像をアップロード：
# 1. 濃い青の画像 → 赤黒くなっていないか確認
# 2. 明るい色の画像 → 淡い青になっていないか確認
# 3. 多色画像 → 自然な色で表示されるか確認
```

## ログの確認

```bash
tail -f /tmp/display_manager.log

# 以下のようなメッセージが表示されるはず：
# "Preparing image for E Ink Spectra 6 display (NO color modification)"
# "Using Waveshare getbuffer() for color conversion and dithering..."
```

## まとめ

**複雑を捨てて、シンプルに。**

Waveshareの公式実装は、数千のハードウェアユニットでテストされています。
私たちの複雑な色処理は、むしろ問題を引き起こしていました。

新しいアプローチ：
- 信頼できる
- 保守性が高い
- 高速
- 予測可能

すべての色処理は、専門家（Waveshare）に任せましょう。
