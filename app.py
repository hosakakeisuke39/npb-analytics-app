
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NPB Batting Analytics",
    page_icon="⚾",
    layout="wide"
)

st.title("⚾ NPB選手成績分析アプリ")
st.caption("学習用の架空データです。実際のNPB公式記録ではありません。")

# 1. CSVを読み込む
csv_path = Path(__file__).parent / "batting.csv"
df = pd.read_csv(csv_path)

# 2. 必要な列が存在するか確認
required = [
    "player", "team", "PA", "AB", "H",
    "2B", "3B", "HR", "BB", "HBP", "SF"
]

missing = [c for c in required if c not in df.columns]

if missing:
    st.error(f"必要な列がありません：{missing}")
    st.stop()

# 3. 数値の検証
numeric_cols = [
    "PA", "AB", "H", "2B", "3B",
    "HR", "BB", "HBP", "SF"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 必須情報の欠損を確認
valid = df[required].notna().all(axis=1)

# 選手名と球団名の空文字も除外
for col in ["player", "team"]:
    valid &= df[col].astype(str).str.strip().ne("")

# 負数や小数の記録を除外
for col in numeric_cols:
    valid &= df[col].ge(0)
    valid &= df[col].mod(1).eq(0)

# 野球記録としての整合性を確認
valid &= df["H"].le(df["AB"])
valid &= (
    df["2B"] + df["3B"] + df["HR"]
).le(df["H"])
valid &= (
    df["AB"] + df["BB"] + df["HBP"] + df["SF"]
).le(df["PA"])

invalid_count = int((~valid).sum())

if invalid_count:
    st.warning(
        f"不正・欠損のある{invalid_count}行を分析から除外しました。"
    )

df = df.loc[valid].copy()

if df.empty:
    st.error("分析できるデータがありません。")
    st.stop()

# 4. 指標を計算（ゼロ除算を防ぐ）
ab = df["AB"].replace(0, float("nan"))
obp_den = (
    df["AB"] + df["BB"] + df["HBP"] + df["SF"]
).replace(0, float("nan"))

df["AVG"] = df["H"] / ab

df["OBP"] = (
    df["H"] + df["BB"] + df["HBP"]
) / obp_den

singles = (
    df["H"] - df["2B"] - df["3B"] - df["HR"]
)

total_bases = (
    singles + 2 * df["2B"]
    + 3 * df["3B"] + 4 * df["HR"]
)

df["SLG"] = total_bases / ab
df["OPS"] = df["OBP"] + df["SLG"]

# 5. フィルター
st.header("📊 成績ランキング")

metric = st.selectbox(
    "比較指標",
    ["OPS", "AVG", "OBP", "SLG"]
)

team = st.selectbox(
    "球団",
    ["全チーム"] + sorted(df["team"].unique().tolist())
)

max_pa = int(df["PA"].max()) + 100

min_pa = st.slider(
    "最低打席数",
    min_value=0,
    max_value=max_pa,
    value=0,
    step=10
)

# 6. 条件に合う選手を抽出
filtered = df[df["PA"] >= min_pa].copy()

if team != "全チーム":
    filtered = filtered[
        filtered["team"] == team
    ].copy()

# 指標が計算できない選手はランキングから除外
ranking = filtered.dropna(subset=[metric])

ranking = ranking.sort_values(
    by=metric,
    ascending=False
).reset_index(drop=True)

ranking["順位"] = ranking.index + 1

# 7. 分析対象数を表示
c1, c2, c3 = st.columns(3)

c1.metric("有効データ数", len(df))
c2.metric("条件該当選手", len(filtered))
c3.metric("ランキング対象", len(ranking))

if ranking.empty:
    st.info("条件を満たす選手がいません。")
    st.stop()

# 8. 成績ランキング
st.subheader(f"{metric}ランキング")

st.dataframe(
    ranking[
        ["順位", "player", "team", "PA", metric]
    ].style.format({metric: "{:.3f}"}),
    hide_index=True
)

# 9. グラフ
st.subheader(f"{metric}比較グラフ")

st.bar_chart(
    ranking,
    x="player",
    y=metric,
    horizontal=True,
    sort=f"-{metric}"
)

# 10. トップ選手
top = ranking.iloc[0]

st.success(
    f"{metric} 1位：{top['player']}"
    f"（{top[metric]:.3f}）"
)

st.caption(
    "最低打席数は任意の分析条件であり、"
    "NPB公式の規定打席を意味しません。"
)
  