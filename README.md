
# NPB Batting Analytics

PythonとStreamlitで開発した野球選手の打撃成績分析アプリです。

※ 現在は学習用の架空データを使用しており、実際のNPB公式記録ではありません。

## 主な機能

- AVG・OBP・SLG・OPSの自動計算
- 選手別成績ランキング
- 球団別フィルター
- 最低打席数フィルター
- 成績比較グラフ
- 不正データ・欠損値の検出

## 使用技術

- Python
- pandas
- Streamlit
- Git / GitHub

## 起動方法

1. `pip install -r requirements.txt`
2. `streamlit run app.py`

## データについて

`batting.csv` は動作確認用の架空データです。

## 今後の改善予定

- NPB公式成績データへの対応
- 複数年度の成績比較
- 選手詳細ページの実装
  