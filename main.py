import streamlit as st
import pandas as pd
import altair as alt
import os

st.title("🌍 MBTI 유형별 국가 Top 10 분석")

# 파일 기본 경로
default_file = "countriesMBTI_16types.csv"

df = None

# 1️⃣ 기본 파일이 있으면 우선 사용
if os.path.exists(default_file):
    df = pd.read_csv(default_file)
    st.success(f"기본 파일 `{default_file}`을 불러왔습니다.")
else:
    # 2️⃣ 없으면 업로드 기능 제공
    uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("업로드한 CSV 파일을 불러왔습니다.")

if df is not None:
    # MBTI 유형 목록
    mbti_types = [
        "INTJ","INTP","ENTJ","ENTP",
        "INFJ","INFP","ENFJ","ENFP",
        "ISTJ","ISFJ","ESTJ","ESFJ",
        "ISTP","ISFP","ESTP","ESFP"
    ]

    # 국가 컬럼 자동 탐색
    country_col = None
    for c in df.columns:
        if c.lower() in ("country","countries","국가","국가명","country_name"):
            country_col = c
            break

    if country_col is None:
        st.error("국가 컬럼을 찾을 수 없습니다. CSV에 'country' 또는 유사한 이름의 컬럼이 있어야 합니다.")
    else:
        # MBTI 유형 선택
        mbti_choice = st.selectbox("MBTI 유형을 선택하세요", mbti_types)

        if mbti_choice not in df.columns:
            st.error(f"선택한 MBTI 유형({mbti_choice}) 데이터가 CSV에 없습니다.")
        else:
            # 비율 계산
            mbti_cols = [c for c in df.columns if c in mbti_types]
            df["_total"] = df[mbti_cols].sum(axis=1)
            df["_ratio"] = df[mbti_choice] / df["_total"]

            # Top 10 국가
            top10 = df[[country_col, mbti_choice, "_ratio"]].sort_values("_ratio", ascending=False).head(10)

            st.subheader(f"{mbti_choice} 비율이 높은 국가 Top 10")

            chart = (
                alt.Chart(top10)
                .mark_bar()
                .encode(
                    x=alt.X("_ratio:Q", title="비율", axis=alt.Axis(format="%")),
                    y=alt.Y(f"{country_col}:N", sort="-x", title="국가"),
                    tooltip=[country_col, mbti_choice, "_ratio"]
                )
                .interactive()
            )

            st.altair_chart(chart, use_container_width=True)

else:
    st.info("기본 파일이 없을 경우, CSV 파일을 업로드해주세요.")
