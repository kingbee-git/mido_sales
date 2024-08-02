# -*- coding: utf-8 -*-
import streamlit as st

import pandas as pd
from datetime import datetime, timedelta

import utils


def make_clickable(val):
    return f'<a target="_blank" href="{val}">{val}</a>'

def news_app():
    news_df = utils.load_news_data()

    today = datetime.now().date()

    st.header(f"뉴스 ({news_df['기사날짜'].min().strftime('%Y-%m-%d')} ~ {today})")
    st.markdown("---")

    key_column = st.selectbox(
        '필터링할 열 선택',
        ['제목', '내용'],
        index=0,
        key='key_column'
    )

    search_term = st.text_input(f'{key_column}에서 검색할 내용 입력', key='search_term')

    if search_term:
        filtered_data = news_df[news_df[key_column].str.contains(search_term, case=False, na=False)]
    else:
        filtered_data = news_df


    news_df['기사날짜'] = pd.to_datetime(news_df['기사날짜']).dt.strftime('%Y-%m-%d')

    st.data_editor(
        filtered_data,
        column_config={
            "URL": st.column_config.LinkColumn(
                "URL",
                display_text="기사 보기",
                help="기사의 원본 링크",
                validate="^https?://",
                max_chars=100
            )
        },
        hide_index=True,
    )