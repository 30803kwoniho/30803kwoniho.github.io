import streamlit as st
import pandas as pd
import altair as alt

@st.cache_data
def load_data():
    try:
        sdr = pd.read_csv("sustainable_development_report_2023.csv")
        owid = pd.read_csv("manufacturing-value-added-to-gdp.csv")
        wb = pd.read_csv("sdg_index_2000-2022.csv")
        return sdr, owid, wb
    except FileNotFoundError as e:
        st.error(f"❌ 파일을 찾을 수 없습니다: {e.filename}")
        return None, None, None

def main():
    st.title("🌍 SDG 9 국가 간 격차 시각화 및 분석")

    sdr, owid, wb = load_data()
    if not all([sdr is not None, owid is not None, wb is not None]):
        st.stop()

    countries = st.multiselect("비교할 국가 선택", sorted(sdr['country'].unique()),
                               default=["Korea, Rep.", "United States", "Kenya"])

    metric = st.selectbox("지표 선택", [
        ("Manufacturing value added (% GDP)", "mfg_value_pct"),
        ("R&D expenditure (% GDP)", "rd_expend_pct"),
        ("Researchers per million", "researchers_pm"),
        ("Mobile network coverage (%)", "mobile_cov_pct")
    ], format_func=lambda x: x[0])

    key = metric[1]

    # 데이터프레임 선택
    if key in owid.columns:
        df = owid
    elif key in sdr.columns:
        df = sdr
    elif key in wb.columns:
        df = wb
    else:
        st.warning("선택한 지표가 어떤 데이터셋에도 존재하지 않습니다.")
        return

    df = df[df['country'].isin(countries)]
    if df.empty:
        st.warning("선택한 지표에 맞는 국가 데이터가 없습니다.")
        return

    # 시각화
    chart = alt.Chart(df).mark_line(point=True).encode(
        x='year:O',
        y=alt.Y(f'{key}:Q', title=metric[0]),
        color='country:N',
        tooltip=['country', 'year', key]
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    # 요약 및 분석
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
