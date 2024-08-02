# -*- coding: utf-8 -*-
import streamlit as st

import numpy as np
import pandas as pd

import utils

def listup_app():
    remain_dep_edu_df, remain_QWGJK_df = utils.load_listup_data()

    st.header("예산 사업 현황")
    st.markdown("---")

    tab1, tab2 = st.tabs(["**지자체 예산 현황**", "**교육청 예산 현황**"])

    with tab1:
        st.header("**지자체 예산 현황**")
        st.markdown("---")

        numeric_columns = ['예산현액', '국비', '시도비', '시군구비', '기타', '지출액', '편성액']

        # 'None'을 NaN으로 대체하고 숫자형으로 변환
        for column in numeric_columns:
            remain_QWGJK_df[column] = remain_QWGJK_df[column].replace('None', np.nan)
            remain_QWGJK_df[column] = pd.to_numeric(remain_QWGJK_df[column].astype(str).str.replace(',', ''), errors='coerce')

        QWGJK_key_column = st.selectbox('필터링할 열 선택', remain_QWGJK_df.columns,
                                        index=remain_QWGJK_df.columns.get_loc('세부사업명'))

        if QWGJK_key_column in numeric_columns:
            min_value = float(remain_QWGJK_df[QWGJK_key_column].min())
            max_value = float(remain_QWGJK_df[QWGJK_key_column].max())
            QWGJK_range = st.slider(f'{QWGJK_key_column}에서 검색할 범위 선택', min_value=min_value, max_value=max_value,
                                    value=(min_value, max_value), key='QWGJK_range')
            QWGJK_filtered_df = remain_QWGJK_df[
                (remain_QWGJK_df[QWGJK_key_column] >= QWGJK_range[0]) & (
                            remain_QWGJK_df[QWGJK_key_column] <= QWGJK_range[1])]
        else:
            QWGJK_search_term = st.text_input(f'{QWGJK_key_column}에서 검색할 내용 입력', key='QWGJK_search_term')
            if QWGJK_search_term:
                QWGJK_filtered_df = remain_QWGJK_df[
                    remain_QWGJK_df[QWGJK_key_column].str.contains(QWGJK_search_term, case=False, na=False)]
            else:
                QWGJK_filtered_df = remain_QWGJK_df

        st.markdown("---")
        QWGJK_editable_df_display = QWGJK_filtered_df[QWGJK_filtered_df['삭제'] == False]
        st.write(f"{len(QWGJK_editable_df_display)} 건")

        edited_data_QWGJK = st.data_editor(
            QWGJK_editable_df_display,
            hide_index=True,
        )

        # 원본 데이터 프레임 업데이트: 인덱스를 기준으로 편집된 데이터 반영
        remain_QWGJK_df.loc[edited_data_QWGJK.index, :] = edited_data_QWGJK

        if st.button('지자체 저장'):
            utils.save_dataframe_to_bigquery(remain_QWGJK_df, 'mido_test', 'remain_QWGJK_df')
            utils.log_user_action(st.session_state['username'], "save list 지자체 현황", "mido_test", "logs")

            st.success('지자체 예산 현황이 성공적으로 저장되었습니다.')


    with tab2:
        st.header("**교육청 예산 현황**")
        st.markdown("---")

        numeric_columns = ['금액', '면적']

        # 'None'을 NaN으로 대체하고 숫자형으로 변환
        for column in numeric_columns:
            remain_dep_edu_df[column] = remain_dep_edu_df[column].replace('None', np.nan)
            remain_dep_edu_df[column] = pd.to_numeric(remain_dep_edu_df[column].astype(str).str.replace(',', ''), errors='coerce')

        dep_edu_key_column = st.selectbox('필터링할 열 선택', remain_dep_edu_df.columns,
                                          index=remain_dep_edu_df.columns.get_loc('과업명'))

        if dep_edu_key_column in numeric_columns:
            min_value = float(remain_dep_edu_df[dep_edu_key_column].min())
            max_value = float(remain_dep_edu_df[dep_edu_key_column].max())
            dep_edu_range = st.slider(f'{dep_edu_key_column}에서 검색할 범위 선택', min_value=min_value, max_value=max_value,
                                      value=(min_value, max_value), key='dep_edu_range')
            dep_edu_filtered_df = remain_dep_edu_df[
                (remain_dep_edu_df[dep_edu_key_column] >= dep_edu_range[0]) & (
                            remain_dep_edu_df[dep_edu_key_column] <= dep_edu_range[1])]
        else:
            dep_edu_search_term = st.text_input(f'{dep_edu_key_column}에서 검색할 내용 입력', key='dep_edu_search_term')
            if dep_edu_search_term:
                dep_edu_filtered_df = remain_dep_edu_df[
                    remain_dep_edu_df[dep_edu_key_column].str.contains(dep_edu_search_term, case=False, na=False)]
            else:
                dep_edu_filtered_df = remain_dep_edu_df

        st.markdown("---")
        dep_edu_editable_df_display = dep_edu_filtered_df[dep_edu_filtered_df['삭제'] == False]
        st.write(f"{len(dep_edu_editable_df_display)} 건")

        edited_data_dep_edu = st.data_editor(
            dep_edu_editable_df_display,
            hide_index=True,
        )

        remain_dep_edu_df.loc[edited_data_dep_edu.index, :] = edited_data_dep_edu

        if st.button('교육청 저장'):
            utils.save_dataframe_to_bigquery(remain_dep_edu_df, 'mido_test', 'remain_dep_edu_df')
            utils.log_user_action(st.session_state['username'], "save list 교육청 현황", "mido_test", "logs")

            st.success('교육청 예산 현황이 성공적으로 저장되었습니다.')