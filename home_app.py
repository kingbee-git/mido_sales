# -*- coding: utf-8 -*-
import streamlit as st

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

import utils

def home_app():
    g2b_data = utils.load_g2b_data()

    current_year = datetime.now().year
    st.header(f"{current_year} 년 납품 현황")

    current_year_data = g2b_data[g2b_data['납품요구접수일자'].dt.year == current_year]

    st.markdown("---")

    current_year_filtered_data = current_year_data[current_year_data['업체명'].str.contains('미도플러스|에코그라운드')]

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    yesterday_data = current_year_filtered_data[current_year_filtered_data['납품요구접수일자'].dt.date <= yesterday]
    today_data = current_year_filtered_data[current_year_filtered_data['납품요구접수일자'].dt.date <= today]

    kpi1, kpi2, kpi3 = st.columns(3)

    if not current_year_data.empty:
        today_count = today_data['수량'].count()
        yesterday_count = yesterday_data['수량'].count()
        count_delta = today_count - yesterday_count
        count_delta_text = f"{count_delta:+,}" if count_delta != 0 else ""
        count_delta_color = "inverse" if count_delta < 0 else "normal" if count_delta > 0 else "off"

        kpi1.metric(
            label="건 수(건)",
            value=f"{today_count:,} 건" if today_count > 0 else "데이터 없음",
            delta=count_delta_text,
            delta_color=count_delta_color
        )

        today_amount = today_data['금액'].sum()
        yesterday_amount = yesterday_data['금액'].sum()
        amount_delta = today_amount - yesterday_amount
        amount_delta_text = f"{amount_delta:+,}" if amount_delta != 0 else ""
        amount_delta_color = "inverse" if amount_delta < 0 else "normal" if amount_delta > 0 else "off"

        kpi2.metric(
            label="금액 합(₩)",
            value=f"₩ {today_amount:,}" if today_amount > 0 else "데이터 없음",
            delta=amount_delta_text,
            delta_color=amount_delta_color
        )

        today_sum = today_data['수량'].sum()
        yesterday_sum = yesterday_data['수량'].sum()
        sum_delta = today_sum - yesterday_sum
        sum_delta_text = f"{sum_delta:+,}" if sum_delta != 0 else ""
        sum_delta_color = "inverse" if sum_delta < 0 else "normal" if sum_delta > 0 else "off"

        kpi3.metric(
            label="수량 합(m²)",
            value=f"{today_sum:,} m²" if today_sum > 0 else "데이터 없음",
            delta=sum_delta_text,
            delta_color=sum_delta_color
        )


    st.markdown("---")

    today_data['납품요구접수일자'] = pd.to_datetime(today_data['납품요구접수일자']).dt.strftime('%Y-%m-%d')

    view_columns = [
        '납품요구접수일자', '수요기관명', '납품요구건명', '업체명', '금액', '수량', '단위', '단가', '품목',
    ]

    key_column = st.selectbox(
        '필터링할 열 선택',
        ['납품요구접수일자', '수요기관명', '납품요구건명', '업체명'],
        index=2
    )

    search_term = st.text_input(f'{key_column}에서 검색할 내용 입력', key='search_term')

    if search_term:
        today_data = today_data[today_data[key_column].str.contains(search_term, case=False, na=False)]

    st.dataframe(
        today_data[view_columns].sort_values(by='납품요구접수일자', ascending=False),
        hide_index=True
    )

    st.markdown("---")

    fig1, space, fig2 = st.columns([10, 1, 10])

    with fig1:
        st.markdown("### 차트")

        total_count = current_year_data['수량'].count()
        total_amount = current_year_data['금액'].sum()

        midoplus_data = current_year_data[current_year_data['업체명'].str.contains('미도플러스')]
        ecoground_data = current_year_data[current_year_data['업체명'].str.contains('에코그라운드')]

        midoplus_count = midoplus_data['수량'].count()
        midoplus_amount = midoplus_data['금액'].sum()

        ecoground_count = ecoground_data['수량'].count()
        ecoground_amount = ecoground_data['금액'].sum()

        midoplus_count_ratio = midoplus_count / total_count if total_count > 0 else 0
        midoplus_amount_ratio = midoplus_amount / total_amount if total_amount > 0 else 0

        ecoground_count_ratio = ecoground_count / total_count if total_count > 0 else 0
        ecoground_amount_ratio = ecoground_amount / total_amount if total_amount > 0 else 0

        comparison_data = pd.DataFrame({
            '업체명': ['전체', '미도플러스', '에코그라운드'],
            '건수': [total_count, midoplus_count, ecoground_count],
            '금액': [total_amount, midoplus_amount, ecoground_amount],
            '건수 비율': ["100%", f"{midoplus_count_ratio:.2%}", f"{ecoground_count_ratio:.2%}"],
            '금액 비율': ["100%", f"{midoplus_amount_ratio:.2%}", f"{ecoground_amount_ratio:.2%}"]
        })

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=comparison_data['업체명'],
            y=comparison_data['금액'],
            name='금액',
            text=[f'업체명: {company}<br>금액: {amount:,}<br>금액 비율: {ratio}' for company, amount, ratio in
                  zip(comparison_data['업체명'], comparison_data['금액'], comparison_data['금액 비율'])],
            textposition='none',
            marker_color='blue',
            opacity=0.6
        ))

        fig.add_trace(go.Scatter(
            x=comparison_data['업체명'],
            y=comparison_data['건수'],
            name='건수',
            mode='lines+markers',
            text=[f'업체명: {company}<br>건수: {count:,}<br>건수 비율: {ratio}' for company, count, ratio in
                  zip(comparison_data['업체명'], comparison_data['건수'], comparison_data['건수 비율'])],
            yaxis='y2',
            line=dict(color='red', width=2, dash='dot'),
            marker=dict(size=8, color='red', opacity=0.7)
        ))

        fig.update_layout(
            xaxis_title='업체',
            yaxis_title='금액',
            yaxis2=dict(
                title='건수',
                overlaying='y',
                side='right',
                showgrid=False
            ),
            xaxis=dict(
                tickmode='array',
                tickvals=[0, 1, 2],
                ticktext=['전체', '미도플러스', '에코그라운드']
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    with fig2:
        st.markdown("### 지도")

        selected_data = current_year_data[current_year_data['업체명'].str.contains('미도플러스|에코그라운드')]

        selected_data = selected_data.dropna(subset=['위도', '경도'])
        selected_data['위도'] = pd.to_numeric(selected_data['위도'], errors='coerce')
        selected_data['경도'] = pd.to_numeric(selected_data['경도'], errors='coerce')
        selected_data = selected_data.dropna(subset=['위도', '경도'])

        if not selected_data.empty:
            size_col = '금액'
            selected_data[size_col] = pd.to_numeric(selected_data[size_col], errors='coerce')

            fig2 = px.scatter_mapbox(
                selected_data,
                lat="위도",
                lon="경도",
                size=size_col,
                color="업체명",
                hover_name="업체명",
                hover_data={size_col: True},
                zoom=5,
                mapbox_style="open-street-map"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.error("위도와 경도 데이터가 필요합니다. 데이터를 확인하세요.")