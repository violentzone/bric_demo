import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def custom_placeholder(text, color):
    return st.markdown(f'<div style="padding: 150px; background-color: #808080; border-radius: 5px;">{text}</div>', unsafe_allow_html=True)

def run():
    st.title("CSV檔案折線圖生成器")


    placeholder = custom_placeholder(" "," ")
    
    # 上傳CSV檔案
    uploaded_file = st.file_uploader("選擇一個CSV檔案", type=["csv"])

    if uploaded_file is not None:
        # 讀取CSV檔案
        df = pd.read_csv(uploaded_file)

        # 第一列當作預設折線
        default_selected_line = df.columns[1]

        # 在側邊欄放置折線選項
        selected_lines = st.sidebar.multiselect("選擇顯示的折線", df.columns[1:], default=[default_selected_line])

        

        # 生成折線圖
        if selected_lines:
            # 生成圖表
            fig, ax = plt.subplots()
            for line in selected_lines:
                ax.plot(df[df.columns[0]], df[line], label=line)
            ax.set_xlabel(df.columns[0])  # 將第一列設為X軸(時間)
            ax.set_title('折線圖')
            ax.legend()  # 圖例
            
            # 使用圖表替代佔位符號
            
            placeholder.pyplot(fig)
        else:
            st.warning("請至少選擇一條折線")

if __name__ == "__main__":
    run()
