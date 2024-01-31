# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 13:04:21 2024

@author: ADMIN
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def main():
    st.title("CSV檔案折線圖生成器")

    # 上傳CSV檔案
    uploaded_file = st.file_uploader("選擇一個CSV檔案", type=["csv"])

    if uploaded_file is not None:
        # 讀取CSV檔案
        df = pd.read_csv(uploaded_file)

        # 顯示資料集
        st.subheader("資料集")
        st.write(df)

        # 選擇欄位
        selected_column = st.selectbox("選擇X軸欄位", df.columns)

        # 顯示圖表選項
        st.subheader("折線圖選項")
        selected_lines = st.multiselect("選擇顯示的折線", df.columns)

        # 生成折線圖
        if selected_lines:
            st.line_chart(df[selected_lines])
            st.pyplot(plt)
        else:
            st.warning("請選擇至少一條折線")

if __name__ == "__main__":
    main()
