# 描画スクリプト実行の修正

## 問題

画像アップロード後に描画スクリプト(`update_display.py`)が実行されない、または失敗している。

## 実施した修正

### 1. サーバー側のログ強化 (`src/server/app.ts`)

**変更箇所:** Line 218-231

**Before:**
```typescript
try {
    await execAsync(`python3 ${DISPLAY_SCRIPT} ${filepath}`);
} catch (error) {
    console.error('Display update failed:', error);
    // Don't fail the upload if display update fails
}
```

**After:**
```typescript
try {
    console.log(`Executing display script: python3 ${DISPLAY_SCRIPT} ${filepath}`);
    const { stdout, stderr } = await execAsync(`python3 ${DISPLAY_SCRIPT} ${filepath}`);
    console.log('Display script stdout:', stdout);
    if (stderr) {
        console.error('Display script stderr:', stderr);
    }
} catch (error) {
    console.error('Display update failed:', error);
    if (error.stdout) console.error('stdout:', error.stdout);
    if (error.stderr) console.error('stderr:', error.stderr);
    // Don't fail the upload if display update fails
}
```

**効果:**
- スクリプトの実行コマンドをログ出力
- stdout/stderrを詳細に記録
- エラー時の診断情報を充実

### 2. 依存関係チェックの追加 (`display/update_display.py`)

**変更箇所:** Line 17-24

**追加されたコード:**
```python
# Check for required dependencies
try:
    import numpy as np
    from PIL import Image
except ImportError as e:
    print(f"ERROR: Missing required dependency: {e}")
    print("Please install: pip3 install numpy pillow")
    sys.exit(1)
```

**効果:**
- numpyとPillowが不足している場合、明確なエラーメッセージ
- インストール方法を提示

### 3. requirements.txt の作成

**新規ファイル:** `requirements.txt`

```
numpy>=1.24.0
Pillow>=10.0.0
psutil>=5.9.0
```

**使用方法:**
```bash
pip3 install -r requirements.txt
```

### 4. 診断テストスクリプトの作成

**新規ファイル:** `test_display_script.sh`

**機能:**
- Python環境の確認
- 依存関係の確認
- スクリプトパスの確認
- 実際に描画スクリプトを実行
- ログファイルの確認
- 診断画像の確認

**使用方法:**
```bash
./test_display_script.sh
```

## トラブルシューティング手順

### ステップ 1: 診断テストを実行

```bash
cd ~/photo_frame
./test_display_script.sh
```

このスクリプトが以下を確認します：
- ✓ Python3がインストールされているか
- ✓ numpy, PIL, psutilがインストールされているか
- ✓ スクリプトファイルが存在するか
- ✓ 描画スクリプトが実行できるか
- ✓ ログファイルの内容

### ステップ 2: 依存関係をインストール

依存関係が不足している場合：

```bash
pip3 install -r requirements.txt
```

### ステップ 3: サーバーログを確認

サーバーを起動して、画像をアップロード時のログを確認：

```bash
cd ~/photo_frame
npm run dev  # 開発環境
# または
npm start    # 本番環境
```

ログに以下が表示されるはず：
```
Executing display script: python3 /path/to/update_display.py /path/to/photo.jpg
Display script stdout: SUCCESS: Display updated
```

### ステップ 4: 手動でスクリプトを実行

```bash
# テスト画像を作成
python3 test_dithering.py

# 手動で描画スクリプトを実行
python3 display/update_display.py /tmp/test_colors_dithered.png
```

成功すると：
```
SUCCESS: Display updated
```

失敗すると：
```
ERROR: <エラーメッセージ>
```

### ステップ 5: ログファイルを確認

```bash
# 描画スクリプトのログ
tail -f /tmp/update_display.log

# ディスプレイマネージャーのログ
tail -f /tmp/display_manager.log
```

## よくある問題と解決策

### 問題 1: "ModuleNotFoundError: No module named 'numpy'"

**原因:** numpyがインストールされていない

**解決策:**
```bash
pip3 install numpy
```

### 問題 2: "ModuleNotFoundError: No module named 'PIL'"

**原因:** Pillowがインストールされていない

**解決策:**
```bash
pip3 install Pillow
```

### 問題 3: "Permission denied"

**原因:** スクリプトに実行権限がない

**解決策:**
```bash
chmod +x display/update_display.py
chmod +x test_display_script.sh
```

### 問題 4: "Image file not found"

**原因:** アップロードされた画像のパスが間違っている

**確認:**
```bash
ls -lh ~/photo_frame/uploads/
```

**app.tsのログを確認:**
```
Executing display script: python3 ... /path/to/photo.jpg
```

### 問題 5: ディザリングが遅すぎる

**原因:** Pi Zero 2 WHでの処理が重い

**一時的な解決策（テスト用）:**

`display_manager.py:346` をコメントアウト:
```python
# dithered_image = apply_floyd_steinberg_dithering(background)
dithered_image = background  # ディザリングなし
```

## 確認項目チェックリスト

デプロイ前に以下を確認：

- [ ] Python3がインストールされている
- [ ] numpy, Pillow, psutilがインストールされている
- [ ] `display/update_display.py`が存在する
- [ ] `display/display_manager.py`が存在する
- [ ] `display/update_display.py`に実行権限がある
- [ ] `uploads/`ディレクトリが存在する
- [ ] テスト画像で手動実行が成功する
- [ ] サーバーログに正しい実行コマンドが表示される

## デプロイ手順

### ステップ 1: コードを取得

```bash
cd ~/photo_frame
git pull origin main
```

### ステップ 2: 依存関係をインストール

```bash
pip3 install -r requirements.txt
```

### ステップ 3: 診断テストを実行

```bash
./test_display_script.sh
```

すべての確認項目が✓なら次へ。

### ステップ 4: サーバーを再起動

```bash
# 開発環境
npm run dev

# 本番環境（systemd使用）
sudo systemctl restart photo-frame
```

### ステップ 5: 画像をアップロードしてテスト

1. ブラウザでアプリを開く
2. 画像をアップロード
3. サーバーログを確認:
   ```
   Executing display script: ...
   Display script stdout: SUCCESS: Display updated
   ```
4. ディスプレイが更新されることを確認

## ログの確認方法

### リアルタイムログ監視

```bash
# ターミナル1: サーバーログ
cd ~/photo_frame
npm run dev

# ターミナル2: 描画スクリプトログ
tail -f /tmp/update_display.log

# ターミナル3: ディスプレイマネージャーログ
tail -f /tmp/display_manager.log
```

### 過去のログ確認

```bash
# 最新20行
tail -20 /tmp/update_display.log
tail -20 /tmp/display_manager.log

# すべて表示
cat /tmp/update_display.log
cat /tmp/display_manager.log
```

## まとめ

**修正内容:**
- ✓ サーバー側のログを強化
- ✓ 依存関係チェックを追加
- ✓ requirements.txtを作成
- ✓ 診断テストスクリプトを作成

**次のステップ:**
1. 診断テストを実行: `./test_display_script.sh`
2. 依存関係をインストール: `pip3 install -r requirements.txt`
3. サーバーを再起動
4. 画像をアップロードしてテスト

**問題が続く場合:**
- ログファイルを確認
- 診断テストの出力を確認
- 手動でスクリプトを実行してエラーメッセージを確認

---

**修正完了: 2025-10-23**
