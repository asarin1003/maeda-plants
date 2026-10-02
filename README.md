# 前田さんの植物写真帖

前田幸男さん（@yukio_maeda）の植物写真投稿をまとめる非公式ギャラリー。

- X APIは使用しません（費用0円）。
- Xの公開syndicationデータから、投稿本文・日時・写真URLをGitHub Actionsで取得します。
- 初期11投稿は `data/posts.json` に登録済みです。
- Actionsは6時間ごとに既登録投稿の情報を更新します。
- 写真をクリックすると元のX投稿を開きます。

## GitHub Pages
Settings → Pages で main branch / root を公開元に指定してください。

## 注意
Xのsyndicationエンドポイントは公式APIではなく、仕様変更で取得できなくなる可能性があります。
