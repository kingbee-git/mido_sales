# -*- coding: utf-8 -*-
import streamlit as st

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

import utils

def home_app():
    g2b_data = utils.load_current_year_g2b_data()

    current_year = datetime.now().year
    st.header(f"{current_year} 년 납품 현황 (미도플러스/에코그라운드)")

    current_year_data = g2b_data[g2b_data['납품요구접수일자'].dt.year == current_year]

    st.markdown("---")

    holidays = [
        '2024-01-01', '2024-02-09', '2024-02-12', '2024-03-01', '2024-04-10', '2024-05-01', '2024-05-05', '2024-05-06',
        '2024-05-15', '2024-06-06', '2024-08-15', '2024-09-16', '2024-09-17', '2024-09-18', '2024-10-03', '2024-10-09',
        '2024-12-25',
        '2025-01-01', '2025-01-28', '2025-01-29', '2025-01-30', '2025-03-01', '2025-03-03', '2025-05-01', '2025-05-05',
        '2025-05-06', '2025-06-06', '2025-08-15', '2025-10-03', '2025-10-06', '2025-10-07', '2025-10-08', '2025-10-09',
        '2025-12-25',
    ]

    def is_holiday(date):
        return date.strftime('%Y-%m-%d') in holidays

    def get_yesterday_with_weekends_and_holidays():
        today = datetime.now()
        yesterday = today - timedelta(2) # 오전에 업데이트 하므로

        if today.weekday() == 0:  # 월요일
            yesterday = today - timedelta(3)  # 금요일
        elif today.weekday() == 6:  # 일요일
            yesterday = today - timedelta(2)  # 금요일
        elif today.weekday() == 5:  # 토요일
            yesterday = today - timedelta(1)  # 금요일

        while is_holiday(yesterday):
            yesterday -= timedelta(1)

        return today.strftime('%Y%m%d'), yesterday.strftime('%Y%m%d')

    today_str, yesterday_str = get_yesterday_with_weekends_and_holidays()

    today = datetime.strptime(today_str, '%Y%m%d').date()
    yesterday = datetime.strptime(yesterday_str, '%Y%m%d').date()

    yesterday_data = current_year_data[current_year_data['납품요구접수일자'].dt.date <= yesterday]
    today_data = current_year_data[current_year_data['납품요구접수일자'].dt.date <= today]

    yesterday_data_filtered = yesterday_data[yesterday_data['업체명'].str.contains('미도플러스|에코그라운드')]
    today_data_filtered = today_data[today_data['업체명'].str.contains('미도플러스|에코그라운드')]

    def format_delta(delta, decimal_points=2):
        if delta > 0:
            color = "green"
            symbol = "▲"
        elif delta < 0:
            color = "red"
            symbol = "▼"
        else:
            color = "black"
            symbol = "-"

        if decimal_points > 0:
            formatted_delta = f"{delta:,.{decimal_points}f}"
        else:
            formatted_delta = f"{delta:,.0f}"

        return f"<span style='color:{color}'>{symbol} {formatted_delta}</span>" if delta != 0 else f"<span style='color:{color}'>{symbol}</span>"

    def display_kpi(label, value, delta, decimal_points=2):
        delta_formatted = format_delta(delta, decimal_points)
        st.markdown(f"""
        <div>
            <span style="font-size: 15px;">{label}</span><br>
            <strong style="font-size: 28px;">{value}</strong><br>
            <span style="font-size: 18px;">{delta_formatted}</span><br><br>
        </div>
        """, unsafe_allow_html=True)

    if not g2b_data.empty:
        kpi1, kpi2, kpi3 = st.columns(3)

        with kpi1:
            today_count = today_data_filtered['수량'].count()
            yesterday_count = yesterday_data_filtered['수량'].count()
            count_delta = today_count - yesterday_count

            display_kpi(
                label="건 수(건)",
                value=f"{today_count:,} 건" if today_count > 0 else "데이터 없음",
                delta=count_delta,
                decimal_points=0  # delta에서 소수점 없음
            )

        with kpi2:
            today_amount = today_data_filtered['금액'].sum()
            yesterday_amount = yesterday_data_filtered['금액'].sum()
            amount_delta = today_amount - yesterday_amount

            display_kpi(
                label="금액 합(₩)",
                value=f"₩ {today_amount:,}" if today_amount > 0 else "데이터 없음",
                delta=amount_delta,
                decimal_points=0  # delta에서 소수점 없음
            )

        with kpi3:
            today_sum = today_data_filtered['수량'].sum()
            yesterday_sum = yesterday_data_filtered['수량'].sum()
            sum_delta = today_sum - yesterday_sum

            display_kpi(
                label="수량 합(m²)",
                value=f"{today_sum:,} m²" if today_sum > 0 else "데이터 없음",
                delta=sum_delta,
                decimal_points=2  # delta에서 소수점 2자리
            )

        kpi4, kpi5, kpi6 = st.columns(3)

        with kpi4:
            today_count_rate = round((today_data_filtered['수량'].count() / today_data['수량'].count()) * 100, 2)
            yesterday_count_rate = round((yesterday_data_filtered['수량'].count() / yesterday_data['수량'].count()) * 100,
                                         2)
            count_rate_delta = today_count_rate - yesterday_count_rate

            display_kpi(
                label="건 (%)",
                value=f"{today_count_rate:,} %" if today_count_rate > 0 else "데이터 없음",
                delta=count_rate_delta,
                decimal_points=2  # delta에서 소수점 2자리
            )

        with kpi5:
            today_amount_rate = round((today_data_filtered['금액'].sum() / today_data['금액'].sum()) * 100, 2)
            yesterday_amount_rate = round((yesterday_data_filtered['금액'].sum() / yesterday_data['금액'].sum()) * 100, 2)
            amount_rate_delta = today_amount_rate - yesterday_amount_rate

            display_kpi(
                label="금액 (%)",
                value=f"{today_amount_rate:,} %" if today_amount_rate > 0 else "데이터 없음",
                delta=amount_rate_delta,
                decimal_points=2  # delta에서 소수점 2자리
            )

        with kpi6:
            today_sum_rate = round((today_data_filtered['수량'].sum() / today_data['수량'].sum()) * 100, 2)
            yesterday_sum_rate = round((yesterday_data_filtered['수량'].sum() / yesterday_data['수량'].sum()) * 100, 2)
            sum_rate_delta = today_sum_rate - yesterday_sum_rate

            display_kpi(
                label="수량 (%)",
                value=f"{today_sum_rate:,} %" if today_sum_rate > 0 else "데이터 없음",
                delta=sum_rate_delta,
                decimal_points=2  # delta에서 소수점 2자리
            )

    st.markdown("---")

    today_data_filtered['납품요구접수일자'] = pd.to_datetime(today_data_filtered['납품요구접수일자']).dt.strftime('%Y-%m-%d')

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
        today_data_filtered = today_data_filtered[today_data_filtered[key_column].str.contains(search_term, case=False, na=False)]

    st.dataframe(
        today_data_filtered[view_columns].sort_values(by='납품요구접수일자', ascending=False),
        hide_index=True
    )

    st.markdown("---")

    fig1, space, fig2 = st.columns([10, 1, 10])

    with fig1:
        st.markdown("### 차트")

        # total_count = current_year_data['수량'].count()
        # total_amount = current_year_data['금액'].sum()
        #
        # midoplus_data = current_year_data[current_year_data['업체명'].str.contains('미도플러스')]
        # ecoground_data = current_year_data[current_year_data['업체명'].str.contains('에코그라운드')]
        #
        # midoplus_count = midoplus_data['수량'].count()
        # midoplus_amount = midoplus_data['금액'].sum()
        #
        # ecoground_count = ecoground_data['수량'].count()
        # ecoground_amount = ecoground_data['금액'].sum()
        #
        # midoplus_count_ratio = midoplus_count / total_count if total_count > 0 else 0
        # midoplus_amount_ratio = midoplus_amount / total_amount if total_amount > 0 else 0
        #
        # ecoground_count_ratio = ecoground_count / total_count if total_count > 0 else 0
        # ecoground_amount_ratio = ecoground_amount / total_amount if total_amount > 0 else 0
        #
        # comparison_data = pd.DataFrame({
        #     '업체명': ['전체', '미도플러스', '에코그라운드'],
        #     '건수': [total_count, midoplus_count, ecoground_count],
        #     '금액': [total_amount, midoplus_amount, ecoground_amount],
        #     '건수 비율': ["100%", f"{midoplus_count_ratio:.2%}", f"{ecoground_count_ratio:.2%}"],
        #     '금액 비율': ["100%", f"{midoplus_amount_ratio:.2%}", f"{ecoground_amount_ratio:.2%}"]
        # })
        #
        # fig = go.Figure()
        #
        # fig.add_trace(go.Bar(
        #     x=comparison_data['업체명'],
        #     y=comparison_data['금액 비율'],
        #     name='금액',
        #     text=[f'업체명: {company}<br>금액: {amount:,}<br>금액 비율: {ratio}' for company, amount, ratio in
        #           zip(comparison_data['업체명'], comparison_data['금액'], comparison_data['금액 비율'])],
        #     textposition='none',
        #     marker_color='blue',
        #     opacity=0.6
        # ))
        #
        # fig.add_trace(go.Scatter(
        #     x=comparison_data['업체명'],
        #     y=comparison_data['건수 비율'],
        #     name='건수',
        #     mode='lines+markers',
        #     text=[f'업체명: {company}<br>건수: {count:,}<br>건수 비율: {ratio}' for company, count, ratio in
        #           zip(comparison_data['업체명'], comparison_data['건수'], comparison_data['건수 비율'])],
        #     line=dict(color='red', width=2, dash='dot'),
        #     marker=dict(size=8, color='red', opacity=0.7)
        # ))
        #
        # fig.update_layout(
        #     xaxis_title='업체',
        #     yaxis_title='금액/건수',
        #     xaxis=dict(
        #         tickmode='array',
        #         tickvals=[0, 1, 2],
        #         ticktext=['전체', '미도플러스', '에코그라운드']
        #     )
        # )
        #
        # st.plotly_chart(fig, use_container_width=True)

        company_amounts = current_year_data.groupby('업체명')['금액'].sum().reset_index()

        fig_amounts = go.Figure(data=[go.Pie(labels=company_amounts['업체명'],
                                             values=company_amounts['금액'],
                                             name='업체별 금액',
                                             textinfo='label+percent',
                                             textposition='outside',
                                             hole=0.3)])

        st.plotly_chart(fig_amounts)


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