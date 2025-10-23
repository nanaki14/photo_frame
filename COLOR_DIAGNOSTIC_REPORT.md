# 色表示診断レポート - Blue appearing yellowish

## 現在の状況

**問題:**
- 赤は正しく表示される ✓
- 青が黄色っぽく表示される ✗

**現在の実装:**
- RGB → BGR 変換を実装済み
- `display_manager.py:312-314` でチャンネルスワップ実行
- `r, g, b = optimized_image.split()`
- `display_image = Image.merge('RGB', (b, g, r))`

## 問題の分析

### 観察された動作

```
Red RGB(255,0,0) → BGR(0,0,255) → 赤に表示 ✓
Blue RGB(0,0,255) → BGR(255,0,0) → 黄色っぽく表示 ✗
```

### 考えられる原因

1. **チャンネル順序がBGRではない**
   - 他の順序の可能性: RBG, GRB, GBR, BRG

2. **Waveshare getbuffer() 内部で追加の色マッピング**
   - ハードウェアが独自の色変換を行っている可能性

3. **6色パレット量子化の問題**
   - Floyd-Steinbergディザリングが予期しない結果を生成

### 重要な洞察

青のBGR変換結果 `(255, 0, 0)` が黄色っぽく見えるということは:

```
期待: BGR(255,0,0) = 赤と認識されるはず（赤のテストで成功したため）
実際: BGR(255,0,0) = 黄色っぽく表示される

これは矛盾している！
```

**可能性:**
- Waveshare getbuffer() がピクセルの位置や周辺ピクセルに基づいて異なる処理を行っている
- 単色画像 vs 複雑な画像で異なる処理パスを使用している
- 内部で追加の色空間変換を実行している

## 作成した診断ツール

### 1. test_color_permutations.py

**目的:** すべての可能なチャンネル順序を体系的にテスト

**作成されたテスト画像:**

#### シンプルテスト（単色）
```
/tmp/test_simple_red.jpg     - RGB(255, 0, 0) 純粋な赤
/tmp/test_simple_blue.jpg    - RGB(0, 0, 255) 純粋な青
/tmp/test_simple_green.jpg   - RGB(0, 128, 0) 純粋な緑
/tmp/test_simple_yellow.jpg  - RGB(255, 255, 0) 純粋な黄色
/tmp/test_simple_black.jpg   - RGB(0, 0, 0) 黒
/tmp/test_simple_white.jpg   - RGB(255, 255, 255) 白
```

#### チャンネル順序テスト
```
/tmp/test_permutation_RGB_Original.jpg   - RGB (元の順序)
/tmp/test_permutation_RBG.jpg            - RBG
/tmp/test_permutation_GRB.jpg            - GRB
/tmp/test_permutation_GBR.jpg            - GBR
/tmp/test_permutation_BRG.jpg            - BRG
/tmp/test_permutation_BGR_Current.jpg    - BGR (現在の実装)
```

## 診断手順

### ステップ 1: シンプルテストの実行（最優先）

以下の画像を**順番に**アップロードして、実際の表示色を記録してください：

```
1. test_simple_red.jpg     → 表示: ?
2. test_simple_blue.jpg    → 表示: ?
3. test_simple_green.jpg   → 表示: ?
4. test_simple_yellow.jpg  → 表示: ?
```

**記録すべき情報:**
- 期待される色
- 実際に表示された色
- 色の近似度（完全一致 / 近い / 全く違う）

### ステップ 2: 結果の分析

シンプルテストの結果から以下を判断：

**パターン A: RGB が正しい**
```
Red → 赤表示 ✓
Blue → 青表示 ✓
Green → 緑表示 ✓
Yellow → 黄色表示 ✓
```
→ BGR変換を削除し、RGBのまま使用

**パターン B: すべて逆**
```
Red → シアン表示
Blue → 黄色表示
Green → マゼンタ表示
```
→ 色反転の可能性

**パターン C: 一部の色だけ正しい**
```
Red → 赤表示 ✓
Blue → 黄色表示 ✗
Green → ?
Yellow → ?
```
→ チャンネル順序テストへ進む

### ステップ 3: チャンネル順序テスト（必要な場合）

シンプルテストでパターンが明確にならない場合、6つの順序テスト画像をアップロード：

```
1. RGB_Original → どの色が正しく表示されるか？
2. RBG → どの色が正しく表示されるか？
3. GRB → どの色が正しく表示されるか？
4. GBR → どの色が正しく表示されるか？
5. BRG → どの色が正しく表示されるか？
6. BGR_Current → どの色が正しく表示されるか？
```

**正しい順序:**
すべての色（赤、緑、青、黄色）が正しく表示される画像の順序

## 既知の情報

### Waveshare Spectra 6 カラーパレット

```python
Black:  RGB(0, 0, 0)
White:  RGB(255, 255, 255)
Red:    RGB(255, 0, 0)
Yellow: RGB(255, 255, 0)
Green:  RGB(0, 128, 0)      # 重要: (0, 255, 0) ではない
Blue:   RGB(0, 0, 255)
```

### 現在の実装（display_manager.py:308-318）

```python
# CRITICAL: Waveshare expects BGR format, but PIL uses RGB
logger.info("Converting RGB to BGR for Waveshare hardware...")

# Split channels and swap R and B
r, g, b = optimized_image.split()
display_image = Image.merge('RGB', (b, g, r))  # BGR order

# Verify conversion
sample_pixel_bgr = display_image.getpixel((10, 10))
logger.info(f"Sample pixel BGR at (10,10): {sample_pixel_bgr} (R and B swapped)")
```

## 次のステップ

1. **シンプルテストを実行** (最優先)
   - 4つのシンプル画像をアップロード
   - 各画像の表示色を記録

2. **結果を報告**
   - どの色が正しく表示されたか
   - どの色が間違って表示されたか
   - 間違った色の詳細（青→黄色など）

3. **修正の適用**
   - 結果に基づいて正しいチャンネル順序を特定
   - `display_manager.py` を更新
   - 再テスト

## テストファイルの場所

すべてのテストファイルは `/tmp/` に作成されました：

```bash
# シンプルテスト
ls /tmp/test_simple_*.jpg

# チャンネル順序テスト
ls /tmp/test_permutation_*.jpg

# カラーテスト（以前作成）
ls /tmp/color_tests/
```

## 予想される解決策

### シナリオ 1: RGBが正しい
```python
# BGR変換を削除
# display_image = optimized_image  # 変換なし
buffer = self.epd.getbuffer(optimized_image)
```

### シナリオ 2: 別の順序が正しい（例: RBG）
```python
r, g, b = optimized_image.split()
display_image = Image.merge('RGB', (r, b, g))  # RBG order
buffer = self.epd.getbuffer(display_image)
```

### シナリオ 3: Waveshare getbuffer() の問題
- Waveshare公式サンプルコードを確認
- epd7in3f.py の getbuffer() 実装を調査
- 必要に応じてカスタムバッファ生成を実装

---

**重要:** シンプルテストの結果を報告してください。これにより正確な解決策を決定できます。
