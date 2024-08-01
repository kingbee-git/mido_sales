# -*- coding: utf-8 -*-
import streamlit as st

import numpy as np
import pandas as pd
import plotly.express as px

import utils

def stat_app():
    g2b_data = utils.load_g2b_data()

    # CSS 스타일링
    st.markdown("""
        <style>
            .stMultiSelect {
                height: 65px;
                overflow-y: auto;
            }
            .stMultiSelect div {
                font-size: 18px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.header("종합쇼핑몰 납품요구 상세내역 통계")
    st.markdown("---")

    # 체크박스: 우수제품여부
    excellent_products = st.checkbox("우수제품여부", value=False)

    if excellent_products:
        filtered_data = g2b_data[g2b_data['우수제품여부'] == 'Y']
    else:
        filtered_data = g2b_data

    col1, space, col2 = st.columns([5, 0.1, 1])

    with col1:
        # 멀티셀렉트: 업체명
        unique_companies = sorted(filtered_data['업체명'].unique())
        selected_companies = st.multiselect("업체명 선택:", unique_companies, default=unique_companies)

        if selected_companies:
            filtered_data = filtered_data[filtered_data['업체명'].isin(selected_companies)]

        else:
            filtered_data = filtered_data

        # 멀티셀렉트: 지역명
        unique_regions = sorted(filtered_data['도광역시'].unique())
        selected_regions = st.multiselect("지역 선택:", unique_regions, default=unique_regions)

        if selected_companies:
            filtered_data = filtered_data[filtered_data['도광역시'].isin(selected_regions)]

        else:
            filtered_data = filtered_data

        date_col1, date_col2, date_col3 = st.columns([5, 1, 1])

        with date_col1:
            # 멀티셀렉트: 연도
            unique_years = pd.to_datetime(filtered_data['납품요구접수일자'], errors='coerce').dt.year.dropna().unique()
            selected_years = st.multiselect("연도 선택:", unique_years, default=unique_years)

            if selected_years:
                filtered_data = filtered_data[pd.to_datetime(filtered_data['납품요구접수일자'], errors='coerce').dt.year.isin(selected_years)]

            min_date = pd.to_datetime(filtered_data['납품요구접수일자'].min(), errors='coerce')
            max_date = pd.to_datetime(filtered_data['납품요구접수일자'].max(), errors='coerce')

        with date_col2:
            # 캘린더: 세부 기간
            min_date = min_date if not pd.isna(min_date) else pd.to_datetime('2000-01-01')
            start_date = st.date_input("시작 날짜:", value=min_date)
        with date_col3:
            max_date = max_date if not pd.isna(max_date) else pd.to_datetime('2100-12-31')
            end_date = st.date_input("종료 날짜:", value=max_date)

        # 기간 유효성 체크
        if start_date > end_date:
            pass

        if start_date and end_date:
            filtered_data = filtered_data[
                (pd.to_datetime(filtered_data['납품요구접수일자'], errors='coerce') >= pd.to_datetime(start_date)) &
                (pd.to_datetime(filtered_data['납품요구접수일자'], errors='coerce') <= pd.to_datetime(end_date))
            ]

    with col2:
        # 슬라이더 추가: 단가, 수량, 금액
        if not filtered_data.empty:
            min_price = float(filtered_data['단가'].min()) if not filtered_data['단가'].isna().all() else 0.0
            max_price = float(filtered_data['단가'].max()) if not filtered_data['단가'].isna().all() else 0.0
            price_range = (min_price, max_price) if min_price < max_price else (0.0, max_price)

            min_quantity = float(filtered_data['수량'].min()) if not filtered_data['수량'].isna().all() else 0.0
            max_quantity = float(filtered_data['수량'].max()) if not filtered_data['수량'].isna().all() else 0.0
            quantity_range = (min_quantity, max_quantity) if min_quantity < max_quantity else (0.0, max_quantity)

            min_amount = float(filtered_data['금액'].min()) if not filtered_data['금액'].isna().all() else 0.0
            max_amount = float(filtered_data['금액'].max()) if not filtered_data['금액'].isna().all() else 0.0
            amount_range = (min_amount, max_amount) if min_amount < max_amount else (0.0, max_amount)

            min_price, max_price = st.slider("단가 범위 선택:", min_price, max_price, price_range)
            min_quantity, max_quantity = st.slider("수량 범위 선택:", min_quantity, max_quantity, quantity_range)
            min_amount, max_amount = st.slider("금액 범위 선택:", min_amount, max_amount, amount_range)

            filtered_data = filtered_data[
                (filtered_data['단가'] >= min_price) & (filtered_data['단가'] <= max_price) &
                (filtered_data['수량'] >= min_quantity) & (filtered_data['수량'] <= max_quantity) &
                (filtered_data['금액'] >= min_amount) & (filtered_data['금액'] <= max_amount)
            ]
        else:
            pass

    st.markdown("---")

    kpi1, kpi2, kpi3 = st.columns(3)

    if not filtered_data.empty:
        avg_price = filtered_data['단가'].mean()
        avg_quantity = filtered_data['수량'].mean()
        avg_amount = filtered_data['금액'].mean()

        kpi1.metric(
            label="단가 평균",
            value=f"₩{round(avg_price, 2):,}" if not pd.isna(avg_price) else "데이터 없음",
            delta=f"₩{round(g2b_data['단가'].mean(), 2):,}" if not pd.isna(g2b_data['단가'].mean()) else "데이터 없음",
            delta_color="inverse" if avg_price < g2b_data['단가'].mean() else "normal"
        )

        kpi2.metric(
            label="수량 평균(m²)",
            value=f"{round(avg_quantity, 2):,}" if not pd.isna(avg_quantity) else "데이터 없음",
            delta=f"{round(g2b_data['수량'].mean(), 2):,}" if not pd.isna(g2b_data['수량'].mean()) else "데이터 없음",
            delta_color="inverse" if avg_quantity < g2b_data['수량'].mean() else "normal"
        )

        kpi3.metric(
            label="금액 평균",
            value=f"₩{round(avg_amount, 2):,}" if not pd.isna(avg_amount) else "데이터 없음",
            delta=f"₩{round(g2b_data['금액'].mean(), 2):,}" if not pd.isna(g2b_data['금액'].mean()) else "데이터 없음",
            delta_color="inverse" if avg_amount < g2b_data['금액'].mean() else "normal"
        )

        kpi4, kpi5, kpi6 = st.columns(3)

        kpi4.metric(
            label="거래 건",
            value=f"{filtered_data['단가'].count():,}",
            delta=f"{g2b_data['단가'].count():,}",
            delta_color="inverse" if filtered_data['단가'].count() < g2b_data['단가'].count() else "normal"
        )

        kpi5.metric(
            label="수량 합 (m²)",
            value=f"{round(filtered_data['수량'].sum(), 2):,}" if not pd.isna(filtered_data['수량'].sum()) else "데이터 없음",
            delta=f"{round(g2b_data['수량'].sum(), 2):,}" if not pd.isna(g2b_data['수량'].sum()) else "데이터 없음",
            delta_color="inverse" if filtered_data['수량'].sum() < g2b_data['수량'].sum() else "normal"
        )

        kpi6.metric(
            label="금액 합",
            value=f"₩{round(filtered_data['금액'].sum(), 2):,}" if not pd.isna(filtered_data['금액'].sum()) else "데이터 없음",
            delta=f"₩{round(g2b_data['금액'].sum(), 2):,}" if not pd.isna(g2b_data['금액'].sum()) else "데이터 없음",
            delta_color="inverse" if filtered_data['금액'].sum() < g2b_data['금액'].sum() else "normal"
        )

    st.markdown("---")

    # 색상 팔레트 정의
    color_map = px.colors.qualitative.Plotly
    unique_companies = filtered_data['업체명'].unique()
    color_discrete_map = {company: color_map[i % len(color_map)] for i, company in enumerate(unique_companies)}

    col3, space, col4, space = st.columns([1, 0.1, 1, 5])

    with col3:
        # 차트에 표시할 항목 선택
        metric_to_plot = st.sidebar.radio("차트에 표시할 항목", ("단가", "수량", "금액"))

    with col4:
        # 상위 N개 선택
        unique_companies_count = len(filtered_data['업체명'].unique())
        if unique_companies_count > 1:
            top_n = st.sidebar.slider(
                "상위 N개 업체 선택",
                min_value=1,
                max_value=max(1, unique_companies_count),
                value=min(unique_companies_count, 10)
            )
        elif unique_companies_count == 1:
            top_n = 1
        else:
            top_n = 1

    # 차트 표시
    fig_col1, space, fig_col2 = st.columns([5, 0.1, 5])

    with fig_col1:
        st.markdown("### 차트")

        if metric_to_plot == "단가":
            # 평균 단가 계산
            avg_price = filtered_data.groupby("업체명")["단가"].mean().reset_index()
            # 상위 N개 선택
            top_avg_price = avg_price.nlargest(top_n, '단가')
            fig = px.bar(top_avg_price, x="업체명", y="단가", title=f"상위 {top_n} 업체별 평균 단가 차트", color='업체명',
                         color_discrete_map=color_discrete_map)
            fig.update_layout(yaxis_title="단가 (원)")
        elif metric_to_plot == "수량":
            # 수량 합계 계산
            total_quantity = filtered_data.groupby("업체명")["수량"].sum().reset_index()
            # 상위 N개 선택
            top_total_quantity = total_quantity.nlargest(top_n, '수량')
            fig = px.bar(top_total_quantity, x="업체명", y="수량", title=f"상위 {top_n} 업체별 수량 차트", color='업체명',
                         color_discrete_map=color_discrete_map)
            fig.update_layout(yaxis_title="수량")
        else:
            # 금액 합계 계산
            total_amount = filtered_data.groupby("업체명")["금액"].sum().reset_index()
            # 상위 N개 선택
            top_total_amount = total_amount.nlargest(top_n, '금액')
            fig = px.bar(top_total_amount, x="업체명", y="금액", title=f"상위 {top_n} 업체별 금액 차트", color='업체명',
                         color_discrete_map=color_discrete_map)
            fig.update_layout(yaxis_title="금액 (원)")

        # 모든 값 표시
        fig.update_traces(texttemplate='%{y:.0f}', textposition='outside')

        st.write(fig)

    # 지도에 사용할 데이터도 상위 N개의 회사로 제한
    top_companies = top_avg_price if metric_to_plot == "단가" else top_total_quantity if metric_to_plot == "수량" else top_total_amount
    top_company_names = top_companies['업체명'].tolist()
    valid_data = filtered_data[filtered_data['업체명'].isin(top_company_names)]

    with fig_col2:
        st.markdown("### 지도")

        # NaN 값을 가진 행을 제거
        valid_data = valid_data.dropna(subset=['위도', '경도'])

        # 위도와 경도를 숫자로 변환 (문자열을 숫자로 변환할 수 없는 경우 NaN으로 처리)
        valid_data['위도'] = pd.to_numeric(valid_data['위도'], errors='coerce')
        valid_data['경도'] = pd.to_numeric(valid_data['경도'], errors='coerce')

        # NaN 값을 가진 행 제거
        valid_data = valid_data.dropna(subset=['위도', '경도'])

        if '위도' in valid_data.columns and '경도' in valid_data.columns:
            if metric_to_plot == "단가":
                size_col = '단가'
            elif metric_to_plot == "수량":
                size_col = '수량'
            else:
                size_col = '금액'

            # 데이터 타입 변환
            valid_data[size_col] = pd.to_numeric(valid_data[size_col], errors='coerce')

            fig2 = px.scatter_mapbox(
                valid_data,
                lat="위도",
                lon="경도",
                size=size_col,
                color="업체명",
                color_discrete_map = color_discrete_map,
                hover_name="업체명",
                hover_data={size_col: True},
                zoom=5,
                opacity=0.3,
                mapbox_style="open-street-map"  # 필요시 API 키를 사용하여 변경
            )
            st.write(fig2)
        else:
            st.error("위도와 경도 데이터가 필요합니다. 데이터를 확인하세요.")

    st.markdown("---")

    filtered_data['납품요구접수일자'] = pd.to_datetime(filtered_data['납품요구접수일자']).dt.strftime('%Y-%m-%d')

    view_columns = [
        '납품요구접수일자', '수요기관명', '납품요구건명', '단가', '단위', '수량', '금액', '품목', '업체명'
    ]

    key_column = st.selectbox(
        '필터링할 열 선택',
        ['납품요구접수일자', '수요기관명', '납품요구건명', '업체명'],
        index=2
    )

    search_term = st.text_input(f'{key_column}에서 검색할 내용 입력', key='search_term')

    if search_term:
        filtered_data = filtered_data[filtered_data[key_column].str.contains(search_term, case=False, na=False)]

    # 데이터프레임 출력
    st.dataframe(
        filtered_data[view_columns].sort_values(by='납품요구접수일자', ascending=False),
        hide_index=True
    )