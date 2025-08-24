# デジタルフォトフレーム ソフトウェア設計書

## プロジェクト概要

### 概要
Waveshare 7.3inch e-inkディスプレイとRaspberry Pi Zero 2 WHを使用したスマートフォンから写真をアップロード可能なデジタルフォトフレーム

### 目的
- スマートフォンから簡単に写真をアップロード
- 低消費電力でバッテリー駆動可能
- e-inkディスプレイによる高品質な写真表示
- アップロード後即座にディスプレイに反映
- 操作があるまで最新の画像を常時表示

## 技術スタック

### フロントエンド
- **React 19**: モダンなUIフレームワーク
- **TypeScript**: 型安全性の確保
- **TailwindCSS**: ユーティリティファーストCSSフレームワーク
- **Radix UI**: アクセシブルなUIコンポーネント
- **React Query**: サーバーステート管理
- **React Hook Form**: フォーム管理
- **Zod**: バリデーション

### バックエンド
- **Bun**: 高速JavaScriptランタイム
- **Hono**: 軽量ウェブフレームワーク
- **Sharp**: 画像処理ライブラリ

### ハードウェア
- **Raspberry Pi Zero 2 WH**: メインコンピュータ
- **Waveshare 7.3inch e-ink display**: 表示デバイス

## システムアーキテクチャ

### 全体構成図
```
┌─────────────────┐    WiFi    ┌─────────────────────┐
│   スマートフォン   │ ◀──────▶ │  Raspberry Pi Zero   │
│   (Webブラウザ)   │           │                    │
└─────────────────┘           │ ┌─────────────────┐ │
                               │ │   Web Server    │ │
                               │ │   (Bun + Hono)  │ │
                               │ └─────────────────┘ │
                               │ ┌─────────────────┐ │
                               │ │ Display Manager │ │
                               │ │   (Python)      │ │
                               │ └─────────────────┘ │
                               │ ┌─────────────────┐ │
                               │ │  File Storage   │ │
                               │ │    (Local)      │ │
                               │ └─────────────────┘ │
                               └─────────────────────┘
                                         │
                                         ▼
                               ┌─────────────────────┐
                               │ Waveshare 7.3inch  │
                               │   e-ink Display     │
                               └─────────────────────┘
```

### コンポーネント構成

#### 1. Webアプリケーション (React + TypeScript)
- **PhotoUploader**: 写真アップロード機能
- **GalleryViewer**: 写真一覧表示
- **SettingsPanel**: 表示設定管理
- **StatusMonitor**: システム状態監視

#### 2. APIサーバー (Bun + Hono)
- **画像アップロード**: マルチパート形式での画像受信
- **画像処理**: Sharp を使用したリサイズ・最適化
- **ファイル管理**: ローカルストレージでの画像管理
- **設定管理**: 表示設定の保存・読込

#### 3. ディスプレイマネージャー (Python)
- **e-ink制御**: Waveshareライブラリを使用した画面制御
- **画像更新**: アップロード後の即座な画面更新
- **電源管理**: 低消費電力モードの制御

## 機能要件

### 基本機能
1. **写真アップロード**
   - Webインターフェースからの画像アップロード
   - 対応形式: JPEG, PNG, WebP
   - 最大ファイルサイズ: 10MB
   - フロントエンドでディスプレイサイズに合わせたクロップ処理
   - アップロード後即座にPythonスクリプト呼び出し

2. **写真表示**
   - 最新アップロード画像の常時表示
   - 操作があるまで画像を保持
   - e-inkディスプレイ最適化済み画像の表示

3. **システム管理**
   - 画像履歴管理
   - システム状態監視

### 拡張機能
1. **画像履歴**: 過去にアップロードした画像の閲覧・再表示
2. **バッテリー監視**: 残量表示とアラート
3. **WiFi設定**: ネットワーク設定画面

## API設計

### エンドポイント仕様

#### 画像管理API
```typescript
// 画像アップロード
POST /api/photos
Content-Type: multipart/form-data
Body: { photo: File }
Response: { id: string, filename: string, uploadedAt: string }

// 画像一覧取得
GET /api/photos
Response: { photos: Photo[] }

// 画像削除
DELETE /api/photos/:id
Response: { success: boolean }

// 現在表示中の画像取得
GET /api/photos/current
Response: { photo: Photo | null }
```

#### 設定管理API
```typescript
// 設定取得
GET /api/settings
Response: { settings: Settings }

// 設定更新
PUT /api/settings
Body: { settings: Partial<Settings> }
Response: { settings: Settings }

// 画像表示更新（Python スクリプト呼び出し）
POST /api/display/update
Body: { photoId: string }
Response: { success: boolean, message: string }
```

#### システム状態API
```typescript
// システム状態取得
GET /api/status
Response: { 
  battery: number, 
  storage: StorageInfo, 
  display: DisplayStatus 
}

// ディスプレイ更新状態確認
GET /api/display/status
Response: { 
  isUpdating: boolean,
  lastUpdate: string,
  currentPhoto: string | null
}
```

### データモデル

```typescript
interface Photo {
  id: string;
  filename: string;
  originalName: string;
  size: number;
  width: number;
  height: number;
  uploadedAt: string;
  favorite?: boolean;
}

interface Settings {
  display: {
    brightness: number;
  };
  system: {
    autoDisplayUpdate: boolean;
    keepHistoryDays: number;
  };
}

interface SystemStatus {
  battery: {
    level: number;
    charging: boolean;
  };
  storage: {
    used: number;
    total: number;
    available: number;
  };
  display: {
    currentPhoto: string | null;
    lastUpdate: string;
    status: 'active' | 'updating' | 'error';
  };
}
```

## ファイル構成

```
photo_frame/
├── src/
│   ├── components/
│   │   ├── ui/                 # 共通UIコンポーネント
│   │   ├── PhotoUploader.tsx   # 写真アップロード
│   │   ├── GalleryViewer.tsx   # ギャラリー表示
│   │   ├── SettingsPanel.tsx   # 設定パネル
│   │   └── StatusMonitor.tsx   # ステータス監視
│   ├── lib/
│   │   ├── api.ts             # API クライアント
│   │   ├── types.ts           # TypeScript型定義
│   │   └── utils.ts           # ユーティリティ関数
│   ├── hooks/                 # カスタムフック
│   │   ├── usePhotos.ts
│   │   ├── useSettings.ts
│   │   └── useStatus.ts
│   └── pages/                 # ページコンポーネント
│       ├── Dashboard.tsx
│       ├── Gallery.tsx
│       └── Settings.tsx
├── server/
│   ├── routes/
│   │   ├── photos.ts          # 写真関連API
│   │   ├── settings.ts        # 設定関連API
│   │   └── status.ts          # ステータスAPI
│   ├── services/
│   │   ├── imageProcessor.ts  # 画像処理サービス
│   │   ├── fileManager.ts     # ファイル管理
│   │   └── configManager.ts   # 設定管理
│   └── types/                 # サーバー型定義
├── display/
│   ├── display_manager.py     # ディスプレイ制御
│   ├── image_updater.py      # 画像更新制御
│   └── power_manager.py      # 電源管理
├── storage/
│   ├── photos/               # アップロード画像
│   ├── thumbnails/           # サムネイル
│   └── config/              # 設定ファイル
└── docs/
    ├── DESIGN_DOCUMENT.md    # 設計書（このファイル）
    ├── API_REFERENCE.md      # API仕様書
    └── DEPLOYMENT.md         # デプロイメント手順
```

## 開発フェーズ

### Phase 1: 基本フレームワーク
- [ ] プロジェクト構成の整備
- [ ] 基本APIサーバーの実装
- [ ] フロントエンド基盤の構築
- [ ] 画像アップロード機能

### Phase 2: ディスプレイ統合
- [ ] e-inkディスプレイドライバー統合
- [ ] Python ディスプレイマネージャー実装
- [ ] 画像表示機能の実装
- [ ] APIとディスプレイの連携

### Phase 3: 高度な機能
- [ ] 画像履歴管理機能
- [ ] 設定管理システム
- [ ] ステータス監視機能
- [ ] エラーハンドリング

### Phase 4: 最適化・テスト
- [ ] パフォーマンス最適化
- [ ] バッテリー寿命最適化
- [ ] 統合テスト
- [ ] ユーザビリティテスト

## 非機能要件

### パフォーマンス
- 画像アップロード: 10MB以下の画像を30秒以内で処理
- 画面更新: e-ink特性を考慮した最適化された更新間隔
- メモリ使用量: 512MB以下（Raspberry Pi Zero 2 WH制約）

### 可用性
- 24時間連続稼働
- WiFi接続断からの自動復旧
- 電源断からの自動復旧

### セキュリティ
- ローカルネットワークからのアクセスのみ
- ファイルアップロードの検証
- 不正ファイル形式の拒否

### 保守性
- モジュラー設計
- ログ出力機能
- 設定ファイルによる柔軟な調整

## 次のステップ

1. **環境構築**: 開発環境のセットアップ
2. **基本API実装**: 画像アップロード・管理API
3. **フロントエンド開発**: React コンポーネントの実装
4. **ハードウェア統合**: e-inkディスプレイとの連携
5. **テスト・デプロイ**: 実機での動作確認

この設計書に基づいて、段階的に開発を進めていきます。