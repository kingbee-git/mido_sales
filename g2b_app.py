# -*- coding: utf-8 -*-
import streamlit as st

import pandas as pd
from datetime import datetime, timedelta

import utils

def g2b_app():
    g2b_data = utils.load_g2b_data()

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
        yesterday = today - timedelta(1)

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

    st.header(f"종합쇼핑몰 납품상세 내역 ({g2b_data['납품요구접수일자'].min().strftime('%Y-%m-%d')} ~ {today})")

    st.markdown("---")

    yesterday_data = g2b_data[g2b_data['납품요구접수일자'].dt.date <= yesterday]
    today_data = g2b_data[g2b_data['납품요구접수일자'].dt.date <= today]

    kpi1, kpi2, kpi3 = st.columns(3)

    if not g2b_data.empty:
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

    kpi4, kpi5, kpi6 = st.columns(3)

    yesterday_data_filtered = yesterday_data[yesterday_data['업체명'].str.contains('미도플러스|에코그라운드')]
    today_data_filtered = today_data[today_data['업체명'].str.contains('미도플러스|에코그라운드')]

    if not g2b_data.empty:
        today_count_rate = round((today_data_filtered['수량'].count() / today_data['수량'].count())*100, 2)
        yesterday_count_rate = round((yesterday_data_filtered['수량'].count() / yesterday_data['수량'].count())*100, 2)
        count_rate_delta = today_count_rate - yesterday_count_rate
        count_rate_delta_text = f"{count_rate_delta:+,}" if count_rate_delta != 0 else ""
        count_rate_delta_color = "inverse" if count_rate_delta < 0 else "normal" if count_rate_delta > 0 else "off"

        kpi4.metric(
            label="건 (%)",
            value=f"{today_count_rate:,} %" if today_count_rate > 0 else "데이터 없음",
            delta=count_rate_delta_text,
            delta_color=count_rate_delta_color
        )

        today_amount_rate = round((today_data_filtered['금액'].sum() / today_data['금액'].sum())*100, 2)
        yesterday_amount_rate = round((yesterday_data_filtered['금액'].sum() / yesterday_data['금액'].sum())*100, 2)
        amount_rate_delta = today_amount_rate - yesterday_amount_rate
        amount_rate_delta_text = f"{amount_rate_delta:+,}" if amount_rate_delta != 0 else ""
        amount_rate_delta_color = "inverse" if amount_rate_delta < 0 else "normal" if amount_rate_delta > 0 else "off"

        kpi5.metric(
            label="금액 (%)",
            value=f"{today_amount_rate:,} %" if today_amount_rate > 0 else "데이터 없음",
            delta=amount_rate_delta_text,
            delta_color=amount_rate_delta_color
        )

        today_sum_rate = round((today_data_filtered['수량'].sum() / today_data['수량'].sum())*100, 2)
        yesterday_sum_rate = round((today_data_filtered['수량'].sum() / today_data['수량'].sum())*100, 2)
        sum_rate_delta = today_sum_rate - yesterday_sum_rate
        sum_rate_delta_text = f"{sum_rate_delta:+,}" if sum_rate_delta != 0 else ""
        sum_rate_delta_color = "inverse" if sum_rate_delta < 0 else "normal" if sum_rate_delta > 0 else "off"

        kpi6.metric(
            label="수량 (%)",
            value=f"{today_sum_rate:,} %" if today_sum_rate > 0 else "데이터 없음",
            delta=sum_rate_delta_text,
            delta_color=sum_rate_delta_color
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