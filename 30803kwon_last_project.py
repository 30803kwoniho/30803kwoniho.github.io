import streamlit as st
import pandas as pd
import altair as alt

@st.cache
def load_data():
    sdr = pd.read_csv("data/sdr_scores.csv")
    owid = pd.read_csv("data/ourworldindata_sdg9.csv")
    wb = pd.read_csv("data/worldbank_sdg9.csv")
    return sdr, owid, wb

def main():
    st.title("🌍 SDG 9 국가 간 격차 시각화 및 분석")

    sdr, owid, wb = load_data()
    countries = st.multiselect("비교할 국가 선택", sorted(sdr['country'].unique()), default=["Korea, Rep.", "United States", "Kenya"])

    metric = st.selectbox("지표 선택", [
        ("Manufacturing value added (% GDP)", "mfg_value_pct"),
        ("R&D expenditure (% GDP)", "rd_expend_pct"),
        ("Researchers per million", "researchers_pm"),
        ("Mobile network coverage (%)", "mobile_cov_pct")
    ], format_func=lambda x: x[0])

    key = metric[1]
    df = owid if key in owid.columns else sdr if key in sdr.columns else wb
    df = df[df['country'].isin(countries)]

    if df.empty:
        st.warning("선택한 지표에 맞는 국가 데이터가 없습니다.")
        return

    chart = alt.Chart(df).mark_line(point=True).encode(
        x='year:O', y=alt.Y(f'{key}:Q', title=metric[0]),
        color='country:N', tooltip=['country', 'year', key]
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    st.markdown("### ⏳ 격차 분석 요약")
    latest = df[df['year'] == df['year'].max()]
    best = latest.sort_values(by=key, ascending=False).iloc[0]
    worst = latest.sort_values(by=key, ascending=True).iloc[0]
    gap = best[key] - worst[key]
    st.write(f"- **{latest['year'].max()}년 기준**, 최고 국가: **{best['country']}** ({best[key]:.1f}), 최저 국가: **{worst['country']}** ({worst[key]:.1f}), 격차: **{gap:.1f}**")

    st.markdown("### ✅ 개선 제언")
    st.write("""\
    - **격차가 큰 국가**는 최상위국의 모델(예: 기술 정책, R&D 정책 구조)를 벤치마킹하세요.  
    - **모바일 커버리지 부족국**은 민관 협력 기반 인프라 투자 확대 및 라이선스 정책 개선이 효과적입니다.  
    - **제조업 기반 취약 국가**는 산업 클러스터, 중소기업 지원 확대, 국제 공급망 참여 프로그램이 필요합니다.
    """)

if __name__ == "__main__":
    main()
