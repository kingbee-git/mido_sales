# -*- coding: utf-8 -*-
import streamlit as st

import pandas as pd

import utils

def filter_data(df, key_prefix):
    key_column_index = df.columns.get_loc('공고명공고번호')
    key_column = st.selectbox(
        '필터링할 열 선택',
        df.columns,
        index=key_column_index,
        key=f'selectbox_{key_prefix}'
    )

    if pd.api.types.is_numeric_dtype(df[key_column]):
        min_value = float(df[key_column].min()) if not df[key_column].isna().all() else 0.0
        max_value = float(df[key_column].max()) if not df[key_column].isna().all() else 0.0
        value_range = (min_value, max_value) if min_value < max_value else (0.0, max_value)

        min_value, max_value = st.slider(f'{key_column}에서 검색할 범위 선택',
                                min_value=min_value,
                                max_value=max_value,
                                value=value_range,
                                key=f'slider_{key_prefix}')

        filtered_df = df[(df[key_column] >= min_value) & (df[key_column] <= max_value)]

    else:
        search_term = st.text_input(f'{key_column}에서 검색할 내용 입력', key=f'text_input_{key_prefix}')
        if search_term:
            filtered_df = df[df[key_column].str.contains(search_term, case=False, na=False)]
        else:
            filtered_df = df

    st.write(f"{len(filtered_df)} 건")
    st.dataframe(filtered_df, hide_index=True)

def info21C_app():
    try:
        info_con_df = utils.load_info_con_data()
        info_ser_df = utils.load_info_ser_data()
        info_pur_df = utils.load_info_pur_data()

        st.header(f"인포 21C")
        st.markdown("---")

        tab1, tab2, tab3 = st.tabs(['공사입찰', '용역입찰', '구매입찰'])

        with tab1:
            st.subheader(f"공사입찰")
            st.markdown("---")
            filter_data(info_con_df, 'info_con_df')

        with tab2:
            st.subheader(f"용역입찰")
            st.markdown("---")
            filter_data(info_ser_df, 'info_ser_df')

        with tab3:
            st.subheader(f"구매입찰")
            st.markdown("---")
            filter_data(info_pur_df, 'info_pur_df')

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.stop()