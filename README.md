# SPLYZA Motion Medical Chatbot

SPLYZA Motion Medical ヘルプセンターのナレッジをベースにした、ユーザー向けの自動応答AIチャットボットシステムです。

ナレッジの優先順位は「TUG評価の進め方」「基本操作・各種設定」がメイン、下部の「カスタム動作」（SPLYZA Motion相当機能）がオプションです。

---

## 🚨 【最重要】ナレッジの管理ルールとフォルダ分離について

本プロジェクトでは、チャットボットが回答時に参照する「公開ナレッジ」と、現時点では絶対にチャットボットに含めたくない「非公開・保留ナレッジ」を誤混同させないため、**物理的なフォルダ構成を完全に分離**しています。

### 1. フォルダの使い分け

| フォルダ名 | 役割 | チャットボットへの反映 | 主な対象ファイル |
| :--- | :--- | :---: | :--- |
| **`src/data/knowledge`** | **本番公開ナレッジ**<br>（ボットが学習・回答するデータ） | **あり**<br>(自動読み込み) | Medicalヘルプから同期した公開データ（`01_` TUG / `02_` 基本操作 / `03_`〜`07_` カスタム動作） |
| **`src/data/pending_knowledge`** | **非公開・保留ナレッジ**<br>（ボットに含めたくないデータ） | **絶対になし**<br>(プログラムで完全除外) | いずれ含めるかもしれないが、現時点では非公開にしたいマニュアル、未公開仕様、社内メモ等 |

### 2. なぜフォルダを分けるのか？（安全性への考慮）
- **RAG（検索拡張生成）の誤読防止**:
  チャットボットは `src/data/knowledge` 直下にあるMarkdownファイルのみを読み込んで回答を生成します。そのため、チャットボットに絶対に含めたくない知識は、`src/data/pending_knowledge` フォルダに保管することで**技術的に100%安全に除外**されます。
- **EXCLUDED_CONTENTS.md の自動除外**:
  ヘルプセンター内の「例外（問い合わせフォームのみのページなど）」を記録する `src/data/knowledge/EXCLUDED_CONTENTS.md` についても、チャットボットに誤って読み込まれないよう、システム（`src/app/api/query/route.ts`）側で明示的にスキップする処理が実装されています。

---

## 📁 ディレクトリ構成

```text
projects/splyza-motion-chatbot/
├── src/
│   ├── app/
│   │   └── api/
│   │       └── query/
│   │           └── route.ts         # チャットボットAPI (RAG読み込み・Gemini連携)
│   └── data/
│       ├── knowledge/               # 【公開】チャットボット本番用ナレッジフォルダ
│       │   ├── 00_System_Prompt_... # システムプロンプト（キャラクター設定等）
│       │   ├── 01_TUG / 02_基本操作 # Medicalメイン機能
│       │   ├── 03〜07_Custom_...   # カスタム動作（オプション）
│       │   └── EXCLUDED_CONTENTS.md # 【ボット非公開】ヘルプセンター上の除外例外リスト
│       └── pending_knowledge/       # 【非公開】保留ナレッジ一時保管フォルダ
│           └── 00_About_Pending_... # 保留フォルダの利用ガイド (本ファイル)
├── README.md                        # プロジェクト全体のガイド（本ドキュメント）
├── guidelines_and_specs.md          # 開発・運用仕様書
└── CHATBOT_UPDATE_GUIDE.md          # ナレッジ更新・改善手順書（AIエージェント指示書）
```

---

## 🛠 開発・運用ドキュメント

プロジェクトの保守や更新を行うためのガイドラインが用意されています。

1. **[開発・運用仕様書](guidelines_and_specs.md) (`guidelines_and_specs.md`)**
   - チャットボットの基盤モデル（Gemini 3.5 Flash）、回答の生成パラメータ、回答ロジック（記載がある場合・ない場合の挙動）、有人サポートへの問い合わせ誘導の判断基準などを網羅しています。
2. **[ナレッジ更新・改善ガイドライン](CHATBOT_UPDATE_GUIDE.md) (`CHATBOT_UPDATE_GUIDE.md`)**
   - Notionヘルプセンターが更新された際、PDFからMarkdownへの変換、段組み崩れの補正、境界識別（XML形式）などの具体的な手順を解説しています。AIエージェントへの一括指示プロンプトもコピペ用として用意されています。

---

## 🚀 ローカル起動方法

### 1. 依存関係のインストール
```bash
npm install
```

### 2. 環境変数の設定
ルートディレクトリ（`projects/splyza-motion-chatbot/`）に `.env.local` ファイルを作成し、Gemini APIキーを設定します。

```env
GEMINI_API_KEY=your_actual_gemini_api_key
```

### 3. 開発サーバーの起動
```bash
npm run dev
```
起動後、ブラウザで [http://localhost:3000](http://localhost:3000) にアクセスします。
