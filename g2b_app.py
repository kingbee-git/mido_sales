# -*- coding: utf-8 -*-
import streamlit as st

import pandas as pd
from datetime import datetime, timedelta

import utils

def g2b_app():
    g2b_data = utils.load_g2b_data()

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

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