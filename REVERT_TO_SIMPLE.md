# シンプルな描画に戻しました

## 実施した変更

すべての色処理を削除し、最もシンプルな状態に戻しました。

### 削除した処理

#### 1. 色強化の削除

**削除したコード (display_manager.py:262-276):**
```python
# 削除: 彩度強化
from PIL import ImageEnhance
enhancer = ImageEnhance.Color(background)
background = enhancer.enhance(1.5)

# 削除: コントラスト強化
enhancer = ImageEnhance.Contrast(background)
background = enhancer.enhance(1.2)
```

#### 2. チャンネル変換の削除

**削除したコード (display_manager.py:308-322):**
```python
# 削除: GBR変換
r, g, b = optimized_image.split()
display_image = Image.merge('RGB', (g, b, r))  # GBR order
```

### 現在の実装

**シンプルなアプローチ:**

1. **画像のロード** ✓
2. **リサイズと中央配置** ✓
3. **RGB画像をそのままWaveshareに渡す** ✓
4. **すべての色処理はWaveshareのgetbuffer()に任せる** ✓

```python
# 現在のコード (シンプル版)

# optimize_image_for_eink():
background.save("/tmp/01_original_image.png")
if background.size != (DISPLAY_WIDTH, DISPLAY_HEIGHT):
    background = background.resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), Image.Resampling.LANCZOS)
final_image = background

# display_image():
display_image = optimized_image  # RGB as-is
buffer = self.epd.getbuffer(display_image)
self.epd.display(buffer)
```

## 変更内容の確認

```bash
git diff display/display_manager.py
```

**削除行数:**
- 色強化: 16行削除
- チャンネル変換: 15行削除
- **合計: 31行削除**

## デプロイ手順

### ステップ 1: コードを取得

```bash
cd ~/photo_frame
git pull origin main
```

### ステップ 2: サービスを再起動

```bash
sudo systemctl restart photo-frame
```

### ステップ 3: テスト

通常の写真をアップロードして表示を確認してください。

## 期待される動作

- ✓ RGB画像がそのままWaveshareに渡される
- ✓ チャンネル変換なし
- ✓ 色強化なし
- ✓ Waveshare getbuffer()がすべての色処理を実行
- ✓ 最もシンプルで予測可能な動作

## 今後の方向性

### オプション 1: Waveshareのドキュメントを確認

公式ドキュメントやサンプルコードで推奨される色処理方法を確認する。

### オプション 2: 実際の写真でテスト

単色テスト画像ではなく、実際の写真で色の表示を確認する。
- 風景写真
- 人物写真
- 複数の色が含まれる画像

### オプション 3: ハードウェアの確認

使用しているWaveshareディスプレイのモデルを確認:
```bash
# 環境変数を確認
echo $WAVESHARE_MODEL

# 実際に使用されているモジュールをログで確認
grep "Using epd" /tmp/display_manager.log
```

可能性:
- epd7in3e (HAT (E) - Spectra 6)
- epd7in3f (7-color Spectra)
- epd7in3b (Red/Black/White)
- epd7in3c (Red/Black/White variant)

モデルによって色処理が異なる可能性があります。

## トラブルシューティング

### 問題: まだ色がおかしい

1. **ログを確認:**
```bash
tail -f /tmp/display_manager.log
```

2. **診断画像を確認:**
```bash
# アップロードした画像がどう処理されたか確認
open /tmp/01_original_image.png
```

3. **Waveshareモデルを確認:**
```bash
grep "epd7in3" /tmp/display_manager.log | head -1
```

### 問題: 色が薄い

これは現在のシンプルなアプローチでは意図的に何もしていません。
実際の写真での表示を確認してから、必要に応じて適度な強化を追加できます。

### 問題: 色が反転している

これはハードウェアまたはドライバの問題の可能性があります。
Waveshare公式のサンプルコードと比較する必要があります。

## まとめ

**現在の状態:**
- ✓ すべての色処理を削除
- ✓ RGB画像を直接Waveshareに渡す
- ✓ 最もシンプルな実装

**次のステップ:**
1. 実際の写真で表示をテスト
2. 色の表示を確認
3. 必要に応じて次のアクションを決定

---

**変更完了: 2025-10-23 (シンプル版に戻す)**
