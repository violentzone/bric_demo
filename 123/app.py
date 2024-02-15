# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 17:43:47 2024

@author: ADMIN
"""

import streamlit as st

# 自定义颜色的占位符
def custom_placeholder(text, color):
    return st.markdown(f'<div style="padding: 10px; background-color: {color}; border-radius: 5px;">{text}</div>', unsafe_allow_html=True)

def run():
    st.title("Custom Placeholder Demo")

    # 创建自定义颜色的占位符
    placeholder = custom_placeholder("This is a custom placeholder with a blue background.", "#007bff")

    # 模拟一些操作后替换占位符内容
    st.write("Performing some operations...")

    # 模拟操作后替换占位符内容
    placeholder.empty()  # 清空占位符
    st.success("Operation completed!")

if __name__ == "__main__":
    run()