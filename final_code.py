import pandas as pd
import streamlit as st
import plotly.graph_objs as go
from ta.volatility import BollingerBands
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from datetime import datetime
import ta
import numpy as np
from matplotlib.ticker import FuncFormatter
import plotly.express as px
import streamlit_option_menu
from streamlit_option_menu import option_menu
file_path = 'C:/Users/admin/GPM1_final/data/Price-Vol VN 2015-2023.xlsx'
@st.cache_data
def load_data(file_path):
    all_sheets = pd.read_excel(file_path, sheet_name=None)
    return all_sheets
all_sheets = load_data(file_path)
df_info = all_sheets['Info']
df_price = all_sheets['Price']
df_volume = all_sheets['Volume']
#XỬ LÝ DỮ LIỆU PRICE
df_price['Code'] = df_price['Code'].str.replace('VT:', '').str.replace('\(P\)', '', regex=True)
df_price.rename(columns={'Code': 'Symbol'}, inplace=True)
start_date_index = df_info.columns.get_loc('Start Date')
activity_index = df_info.columns.get_loc('Activity')
df_info_selected = df_info.iloc[:, start_date_index:activity_index + 1]
df_combined = pd.concat([df_price, df_info_selected], axis=1)
df_1 = df_combined[df_combined['Activity'] != 'Dead']
start_date_index = df_1.columns.get_loc('Start Date')
data = df_1.iloc[:, 3:start_date_index]
df = pd.concat([df_1.iloc[:, 1], data], axis=1)
df.rename(columns={'Symbol': 'Date'}, inplace=True)
df.set_index('Date', inplace=True)
df_transposed = df.T
df_dict = {}
for col_name in df_transposed.columns:
    col_df = df_transposed[[col_name]]
    col_df = col_df.dropna()
    df_dict[col_name] = col_df
keys = df_dict.keys()
values = df_dict.values()
#XỬ LÝ DỮ LIỆU VOLUME
df_volume['Code'] = df_volume['Code'].str.replace('VT:', '').str.replace('\(VO\)', '', regex=True)
df_volume.rename(columns={'Code': 'Symbol'}, inplace=True)
df_combined2 = pd.concat([df_volume, df_info_selected], axis=1)
df_2 = df_combined2[df_combined2['Activity'] != 'Dead']
start_date_index = df_2.columns.get_loc('Start Date')
other_data = df_2.iloc[:,3:start_date_index]
df2 = pd.concat([df_2.iloc[:,1],other_data], axis=1)
df2.rename(columns={'Symbol': 'Date'}, inplace=True)
df2.set_index('Date', inplace=True)
df2_transposed = df2.T
df2_dict = {}
for col_name in df2_transposed.columns:
    col_df2 = df2_transposed[[col_name]]
    col_df2 = col_df2.dropna()
    df2_dict[col_name] = col_df2
keys = df2_dict.keys()
values = df2_dict.values()
with st.sidebar:
  selected = option_menu(
    menu_title = "Điều hướng",
    options = ["Phân tích kỹ thuật","Phân tích tài chính doanh nghiệp","Phân tích ngành"])
if selected == "Phân tích kỹ thuật":
    st.header("**PHÂN TÍCH KỸ THUẬT**")
    def get_input():
        stock_symbol = st.text_input("Nhập mã chứng khoán:")
        selected_indicator = st.selectbox("Chọn chỉ báo kỹ thuật",
                                         ["Price and Volume", "Moving Average", "Bollinger Bands", "RSI", "MACD",
                                          "Stochastic Oscillator"])
        return stock_symbol, selected_indicator
    stock_symbol, selected_indicator = get_input()
    cleaned_stock_symbol = stock_symbol.strip().upper()
    if cleaned_stock_symbol in keys:
        df = df_dict[cleaned_stock_symbol.upper()]
        df_volume = df2_dict[cleaned_stock_symbol]
        df.rename(columns={cleaned_stock_symbol: 'close'}, inplace=True)
        if selected_indicator == "Price and Volume":
            fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                                subplot_titles=["Price and Volume"],
                                specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Scatter(x=df.index, y=df.close, name='Price', line=dict(color='orange', width=1)),
                secondary_y=False)
            fig.add_trace(go.Bar(x=df_volume.index, y=df_volume[cleaned_stock_symbol], name='Volume', marker_color='blue'),
                secondary_y=False)
            fig.update_layout(title=f'{cleaned_stock_symbol} Price and Volume',
                              xaxis=dict(rangeslider=dict(visible=True),
                                         rangeselector=dict(
                                             buttons=list([
                                                 dict(count=1, label='1m', step='month', stepmode='backward'),
                                                 dict(count=6, label='6m', step='month', stepmode='backward'),
                                                 dict(count=1, label='YTD', step='year', stepmode='todate'),
                                                 dict(count=1, label='1y', step='year', stepmode='backward'),
                                                 dict(step='all')
                                             ])
                                         )
                                         )
                              )
            st.header(stock_symbol.upper() + " Price and Volume\n")
            st.plotly_chart(fig)
        elif selected_indicator == "Moving Average":
            df['50_SMA'] = df['close'].rolling(window=50).mean()
            df['100_SMA'] = df['close'].rolling(window=100).mean()
            df['200_SMA'] = df['close'].rolling(window=200).mean()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df.close, name='Price', line=dict(color='orange', width=1)))
            fig.add_trace(go.Scatter(x=df.index, y=df['50_SMA'], name='50 MA', line=dict(color='blue', width=0.5)))
            fig.add_trace(go.Scatter(x=df.index, y=df['100_SMA'], name='100 MA', line=dict(color='green', width=0.5)))
            fig.add_trace(go.Scatter(x=df.index, y=df['200_SMA'], name='200 MA', line=dict(color='purple', width=0.5)))
            fig.update_layout(title=f'Moving Average indicator',
                              xaxis=dict(rangeslider=dict(visible=True),
                                         rangeselector=dict(
                                             buttons=list([
                                                 dict(count=1, label='1m', step='month', stepmode='backward'),
                                                 dict(count=6, label='6m', step='month', stepmode='backward'),
                                                 dict(count=1, label='YTD', step='year', stepmode='todate'),
                                                 dict(count=1, label='1y', step='year', stepmode='backward'),
                                                 dict(step='all')
                                             ])
                                         )
                                         )
                              )
            st.header(stock_symbol.upper() + " Moving Average\n")
            st.plotly_chart(fig)
        elif selected_indicator == "Bollinger Bands":
            df['MA'] = df['close'].rolling(window=20).mean()
            df['Upper Band'] = df['MA'] + 2 * df['close'].rolling(window=20).std()
            df['Lower Band'] = df['MA'] - 2 * df['close'].rolling(window=20).std()
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=df.index, y=df['Upper Band'], mode='lines', name='Upper Band', line=dict(color='orange', width=2)))
            fig.add_trace(
                go.Scatter(x=df.index, y=df['Lower Band'], mode='lines', name='Lower Band', line=dict(color='blue', width=2)))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA'], mode='lines', name='MA', line=dict(color='green', width=2)))
            fig.update_layout(title=f'Bollinger Bands indicator',
                              xaxis=dict(rangeslider=dict(visible=True),
                                         rangeselector=dict(
                                             buttons=list([
                                                 dict(count=1, label='1m', step='month', stepmode='backward'),
                                                 dict(count=6, label='6m', step='month', stepmode='backward'),
                                                 dict(count=1, label='YTD', step='year', stepmode='todate'),
                                                 dict(count=1, label='1y', step='year', stepmode='backward'),
                                                 dict(step='all')
                                             ])
                                         )
                                         )
                              )
            st.header(stock_symbol.upper() + " Bollinger Band\n")
            st.plotly_chart(fig)
        elif selected_indicator == "RSI":
            duong_chi_bao = "RSI"
            df["rsi"] = ta.momentum.RSIIndicator(df['close']).rsi()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name='RSI', yaxis='y2',
                                     line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=df.index, y=[70] * len(df), mode='lines',
                                     name='Overbought (70)', yaxis='y2', line=dict(color='red', dash='dash')))
            fig.add_trace(go.Scatter(x=df.index, y=[30] * len(df), mode='lines',
                                     name='Oversold (30)', yaxis='y2', line=dict(color='green', dash='dash')))
            fig.update_layout(title=f'RSI indicator',
                              xaxis=dict(rangeslider=dict(visible=True),
                                         rangeselector=dict(
                                             buttons=list([
                                                 dict(count=1, label='1m', step='month', stepmode='backward'),
                                                 dict(count=6, label='6m', step='month', stepmode='backward'),
                                                 dict(count=1, label='YTD', step='year', stepmode='todate'),
                                                 dict(count=1, label='1y', step='year', stepmode='backward'),
                                                 dict(step='all')
                                             ])
                                         )
                                         ),
                              yaxis=dict(title='Price'),
                              yaxis2=dict(title=f'RSI', overlaying='y', side='right'))
            st.header(stock_symbol.upper() + " RSI\n")
            st.plotly_chart(fig)
        elif selected_indicator == "MACD":
            short_period = 12
            long_period = 26
            signal_period = 9
            df['ShortEMA'] = df['close'].ewm(span=short_period, adjust=False).mean()
            df['LongEMA'] = df['close'].ewm(span=long_period, adjust=False).mean()
            df['MACD'] = df['ShortEMA'] - df['LongEMA']
            df['Signal Line'] = df['MACD'].ewm(span=signal_period, adjust=False).mean()
            df['Histogram'] = df['MACD'] - df['Signal Line']
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD', line=dict(color='orange', width=2)))
            fig.add_trace(go.Scatter(x=df.index, y=df['Signal Line'], mode='lines', name='Signal Line',
                                     line=dict(color='blue', width=2)))
            fig.add_trace(go.Bar(x=df.index, y=df['Histogram'], name='Histogram'))
            fig.update_layout(title=f'MACD Indicator',
                              xaxis=dict(rangeslider=dict(visible=True),
                                         rangeselector=dict(
                                             buttons=list([
                                                 dict(count=1, label='1m', step='month', stepmode='backward'),
                                                 dict(count=6, label='6m', step='month', stepmode='backward'),
                                                 dict(count=1, label='YTD', step='year', stepmode='todate'),
                                                 dict(count=1, label='1y', step='year', stepmode='backward'),
                                                 dict(step='all')
                                             ])
                                         )
                                         )
                              )
            st.header(stock_symbol.upper() + " MACD\n")
            st.plotly_chart(fig)
        elif selected_indicator == "Stochastic Oscillator":
            k_period = 14
            d_period = 3
            df['LowestLow'] = df['close'].rolling(window=k_period).min()
            df['HighestHigh'] = df['close'].rolling(window=k_period).max()
            df['K'] = 100 * (df['close'] - df['LowestLow']) / (df['HighestHigh'] - df['LowestLow'])
            df['D'] = df['K'].rolling(window=d_period).mean()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['K'], mode='lines', name='K',
                                     line=dict(color='orange', width=2)))
            fig.add_trace(go.Scatter(x=df.index, y=df['D'], mode='lines', name='D',
                                     line=dict(color='blue', width=2)))
            fig.update_layout(title=f'Stochastic Oscillator indicator',
                              xaxis=dict(rangeslider=dict(visible=True),
                                         rangeselector=dict(
                                             buttons=list([
                                                 dict(count=1, label='1m', step='month', stepmode='backward'),
                                                 dict(count=6, label='6m', step='month', stepmode='backward'),
                                                 dict(count=1, label='YTD', step='year', stepmode='todate'),
                                                 dict(count=1, label='1y', step='year', stepmode='backward'),
                                                 dict(step='all')
                                             ])
                                         )
                                         )
                              )
            st.header(stock_symbol.upper() + " Stochastic Oscillator\n")
            st.plotly_chart(fig)
        else:
            st.warning("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
    else:
        st.warning("Vui lòng nhập mã chứng khoán bạn muốn.")
elif selected == "Phân tích tài chính doanh nghiệp":
    st.header("**PHÂN TÍCH TÀI CHÍNH DOANH NGHIỆP**")
    def clean_data(file_path):
        df = pd.read_excel(file_path)
        df = df.iloc[7:, :]
        df.columns = df.iloc[0]
        df.columns.name = None
        df = df.iloc[1:, :]
        df.reset_index(drop=True, inplace=True)
        new_column_names = [col.split('\n')[0] for col in df.columns]
        df.columns = new_column_names
        index_to_keep = df[df['STT'] == 1664].index[0]
        df = df.loc[:index_to_keep]
        df['Năm'] = df['Năm'].apply(lambda x: str(x).replace(',', ''))
        return df
    def load_and_display_data(dfs, stock_code, report_tables):
        stock_data = pd.DataFrame()
        for df_name, df in dfs.items():
            important_columns = [col for col in df.columns for table in report_tables if col.startswith(table + '.')]
            stock_year_data = df[df['Mã'] == stock_code]
            stock_year_data = stock_year_data[
                ['Năm', 'Mã', 'Tên công ty', 'Sàn', 'Ngành ICB - cấp 3'] + important_columns]
            stock_year_data = stock_year_data.loc[:, ~stock_year_data.columns.duplicated()]
            stock_data = pd.concat([stock_data, stock_year_data])
        stock_data['Năm'] = stock_data['Năm'].astype(int)
        stock_data.sort_values(by='Năm', inplace=True)
        stock_data['Năm'] = stock_data['Năm'].apply(lambda x: int(x.replace(',', '')) if isinstance(x, str) else x)
        stock_data.reset_index(drop=True, inplace=True)
        return stock_data
    def display_stock_data(stock_code):
        report_tables = ['CĐKT', 'KQKD', 'LCTT', 'TM', 'BCTCKH']
        result_data = load_and_display_data(dfs, stock_code, report_tables)
        return result_data
    file_paths = ["C:/Users/admin/GPM1_final/data/2022-Vietnam.xlsx",
                  "C:/Users/admin/GPM1_final/data/2021-Vietnam.xlsx",
                  "C:/Users/admin/GPM1_final/data/2020-Vietnam.xlsx",
                  "C:/Users/admin/GPM1_final/data/2019-Vietnam.xlsx",
                  "C:/Users/admin/GPM1_final/data/2018-Vietnam.xlsx"]
    dfs = {}
    for file_path in file_paths:
        year = file_path.split('/')[-1].split('-')[0]
        dfs[f"df_{year}"] = clean_data(file_path)
    df = display_stock_data('MWG')
    df = df.rename(columns={
        'KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp': 'Lợi nhuận sau thuế thu nhập doanh nghiệp (KQKD)',
        'KQKD. Tổng lợi nhuận kế toán trước thuế': 'Tổng lợi nhuận kế toán trước thuế (KQKD)',
        'KQKD. Trong đó: Chi phí lãi vay': 'Chi phí lãi vay',
        'CĐKT. Tiền và tương đương tiền ': 'Tiền và tương đương tiền (CĐKT)'
    })
    new_columns = [col.split('.')[-1] for col in df.columns]
    df.rename(columns=dict(zip(df.columns, new_columns)), inplace=True)
    result_df = df.copy()
    result_df.columns = result_df.columns.str.strip()
    if 'current_tab_doanh_nghiep' not in st.session_state:
        st.session_state['current_tab_doanh_nghiep'] = 'Tổng quan doanh nghiệp'
    col1, spacer1, col2, spacer2, col3 = st.columns([0.5, 0.5, 0.5, 0.5, 0.5])
    with col1:
        option_tong_quan = st.button("Tổng quan doanh nghiệp")
    with col2:
        option_chi_so = st.button("Số liệu tài chính")
    with col3:
        option_bieu_do = st.button("Biểu đồ tài chính")
    if option_tong_quan:
        st.session_state['current_tab_doanh_nghiep'] = 'Tổng quan doanh nghiệp'
    elif option_chi_so:
        st.session_state['current_tab_doanh_nghiep'] = 'Số liệu tài chính'
    elif option_bieu_do:
        st.session_state['current_tab_doanh_nghiep'] = 'Biểu đồ tài chính'
    st.write("\n"
             "\n")
    if st.session_state['current_tab_doanh_nghiep'] == 'Tổng quan doanh nghiệp':
        st.markdown("""
                <style>
                .container {
                    display: flex;
                    justify-content: space-between;
                }
                .info-container, .leadership-container {
                    background-color: #f0f2f6;
                    border-radius: 10px;
                    padding: 20px;
                    margin-bottom: 20px;
                    width: 49%; 
                }
                .info-row, .leadership-row {
                    margin-bottom: 10px;
                }
                .info-label, .leadership-title {
                    font-weight: bold;
                    display: inline-block; 
                    margin-right: 15px; 
                }
                .info, .leadership-name {
                    display: inline-block;
                    text-align: left;
                }
                </style>
                """, unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: justify;'>"
            "Công ty cổ phần Đầu tư Thế Giới Di Động (MWG) được thành lập từ tháng 03/2004, với tiền thân là Công ty "
            "trách nhiệm hữu hạn Thế Giới Di Động. Công ty quản lý vận hành các chuỗi cửa hàng bán lẻ Thế Giới Di Động, "
            "Điện Máy Xanh, Bách Hoá Xanh, nhà thuốc An Khang với mạng lưới 5.750 cửa hàng trên toàn quốc."
            "</p>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align: justify;'>"
            "Sau gần 10 năm hoạt động, MWG đã trở thành nhà bán lẻ điện thoại di động lớn nhất Việt Nam với 217 cửa hàng "
            "phủ khắp 63 tỉnh thành. Doanh số điện thoại bán ra đạt gần 300.000 máy/tháng. Đến nay, MWG là đơn vị duy nhất "
            "có hệ thống cửa hàng bán lẻ điện thoại đi động phủ khắp 63 tỉnh thành phố tại Việt Nam. MWG đã tự xây dựng hệ "
            "thống công nghệ thông tin hiện đại phục vụ cho hoạt động kinh doanh của mình. Các hệ thống đang được công ty áp "
            "dụng là hệ thống kiểm soát nội bộ ERP, hệ thống kiểm soát an ninh bằng camera... MWG luôn chú trọng vào việc "
            "nâng cao chất lượng phục vụ, đem lại nhiều hơn nữa giá trị cho khách hàng."
            "</p>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='container'>"
            "<div class='info-container'>"
            "<div class='info-row'><span class='info-label'>Tên công ty:</span><span class='info'>CTCP Đầu tư Thế giới Di động</span></div>"
            "<div class='info-row'><span class='info-label'>Ngành cấp 1:</span><span class='info'>Dịch vụ tiêu dùng</span></div>"
            "<div class='info-row'><span class='info-label'>Ngành cấp 2:</span><span class='info'>Bán lẻ</span></div>"
            "<div class='info-row'><span class='info-label'>Ngành cấp 3:</span><span class='info'>Bán lẻ</span></div>"
            "<div class='info-row'><span class='info-label'>Ngành cấp 4:</span><span class='info'>Phân phối hàng chuyên dụng</span></div>"
            "<div class='info-row'><span class='info-label'>Sàn giao dịch:</span><span class='info'>HOSE</span></div>"
            "<div class='info-row'><span class='info-label'>Ngày niêm yết:</span><span class='info'>14/07/2014</span></div>"
            "<div class='info-row'><span class='info-label'>Vốn hoá:</span><span class='info'>61,281.27 tỷ đồng</span></div>"
            "<div class='info-row'><span class='info-label'>Số lượng nhân sự:</span><span class='info'>74,111</span></div>"
            "<div class='info-row'><span class='info-label'>DVKT năm gần nhất:</span><span class='info'>EY</span></div>"
            "</div>"
            "<div class='leadership-container'>"
            "<p class='leadership-title'>Ban lãnh đạo:</p>"
            "<p class='leadership-row'><span class='leadership-name'>Nguyễn Đức Tài - Chủ tịch HĐQT</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Đoàn Văn Hiểu Em - Thành viên HĐQT</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Đào Thế Vinh - Thành viên HĐQT</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Trần Huy Thanh Tùng - Thành viên HĐQT</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Robert Alan Willett - Thành viên HĐQT</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Đào Minh Lượm - Thành viên HĐQT</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Đỗ Tiến Sĩ - Thành viên HĐQT</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Nguyễn Tiến Trung - Thành viên HĐQT</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Thomas Lanyi - Thành viên HĐQT</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Lê Thị Thu Trang - Người phụ trách quản trị công ty</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Nguyễn Tiến Trung - Chủ tịch Ủy ban kiểm toán</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Đào Thế Vinh - Thành viên Ủy ban kiểm toán</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Trần Huy Thanh Tùng - Tổng giám đốc</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Vũ Đăng Linh - Giám đốc tài chính</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Điêu Chính Hải Triều - Giám đốc kỹ thuật</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Lý Trần Kim Ngân - Kế toán trưởng</span></p>"
            "<p class='leadership-row'><span class='leadership-name'>Lê Thị Thu Trang - Đại diện công bố thông tin</span></p>"
            "</div>"
            "</div>",
            unsafe_allow_html=True
        )

    elif st.session_state['current_tab_doanh_nghiep'] == 'Số liệu tài chính':
        stock_data = display_stock_data('MWG')

        if stock_data['Năm'].dtype != 'object':
            stock_data['Năm'] = stock_data['Năm'].astype(str)
        stock_data['Năm'] = stock_data['Năm'].str.replace(',', '').astype(int)

        cdk_columns = [col for col in stock_data.columns if col.startswith('CĐKT.')]
        if cdk_columns:
            st.write("### Cân đối kế toán")
            st.dataframe(stock_data[['Năm', 'Mã', 'Tên công ty', 'Sàn', 'Ngành ICB - cấp 3'] + cdk_columns])
        kqkd_columns = [col for col in stock_data.columns if col.startswith('KQKD.')]
        if kqkd_columns:
            st.write("### Kết quả kinh doanh")
            st.dataframe(stock_data[['Năm', 'Mã', 'Tên công ty', 'Sàn', 'Ngành ICB - cấp 3'] + kqkd_columns])
        lctt_columns = [col for col in stock_data.columns if col.startswith('LCTT.')]
        if lctt_columns:
            st.write("### Lưu chuyển tiền tệ")
            st.dataframe(stock_data[['Năm', 'Mã', 'Tên công ty', 'Sàn', 'Ngành ICB - cấp 3'] + lctt_columns])
        tm_columns = [col for col in stock_data.columns if col.startswith('TM.')]
        if tm_columns:
            st.write("### Thuyết minh")
            st.dataframe(stock_data[['Năm', 'Mã', 'Tên công ty', 'Sàn', 'Ngành ICB - cấp 3'] + tm_columns])
    elif st.session_state['current_tab_doanh_nghiep'] == 'Biểu đồ tài chính':
        # TĂNG TRƯỞNG DOANH THU
        result_df['Doanh thu %'] = result_df['Doanh thu thuần'].pct_change() * 100
        fig = go.Figure()
        fig.add_trace(
            go.Bar(x=result_df['Năm'], y=result_df['Doanh thu thuần'] / 1e9, name='Doanh thu thuần', yaxis='y1',
                   width=0.4,marker=dict(color='#FFC0D9'),
                   hovertemplate='Năm: %{x}<br>Doanh thu thuần: %{y:.4s} tỷ VND<extra></extra>',
                   text=[f"{y:,.2f}" for y in result_df['Doanh thu thuần'] / 1e9],
                   textposition='outside'))
        fig.add_trace(
            go.Scatter(x=result_df['Năm'], y=result_df['Doanh thu %'], name='Doanh thu thuần (YoY)', yaxis='y2',
                       hovertemplate='Năm: %{x}<br>Doanh thu thuần (YoY): %{y:.2f}%<extra></extra>',
                       mode='lines+markers+text',line=dict(color='#30B8B8'),
                       text=[f"{y:.2f}%" for y in result_df['Doanh thu %']], textposition='top center'))
        fig.update_layout(title='TĂNG TRƯỞNG DOANH THU', xaxis=dict(title='Năm'),
                          yaxis=dict(title='Doanh thu thuần (tỷ VND)', tickformat=',d'),
                          yaxis2=dict(title='Doanh thu thuần YoY (%)', overlaying='y', side='right', showgrid=False,
                                      showline=False, zeroline=False),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), barmode='group')
        st.plotly_chart(fig)

        # TĂNG TRƯỞNG LỢI NHUẬN
        result_df['Lợi nhuận sau thuế %'] = result_df['Lợi nhuận sau thuế thu nhập doanh nghiệp (KQKD)'].pct_change() * 100
        fig = go.Figure()
        formatted_labels = [f"{y:,.2f}" for y in result_df['Lợi nhuận sau thuế thu nhập doanh nghiệp (KQKD)'] / 1e9]
        fig.add_trace(go.Bar(x=result_df['Năm'], y=result_df['Lợi nhuận sau thuế thu nhập doanh nghiệp (KQKD)'] / 1e9,
                             name='Lợi nhuận sau thuế', yaxis='y1',
                             marker=dict(color='#4FC0D0'), width=0.4,
                             hovertemplate='Năm: %{x}<br>Lợi nhuận sau thuế: %{y:.2f} tỷ VND<extra></extra>',
                             text=formatted_labels, textposition='outside'))
        fig.add_trace(
            go.Scatter(x=result_df['Năm'], y=result_df['Lợi nhuận sau thuế %'], name='Lợi nhuận sau thuế (YoY)',
                       yaxis='y2', hovertemplate='Năm: %{x}<br>Lợi nhuận sau thuế (YoY): %{y:.2f}%<extra></extra>',
                       mode='lines+markers+text', marker=dict(color='#9085BD'),text=[f"{y:.2f}%" for y in result_df['Lợi nhuận sau thuế %']],
                       textposition='top center'))
        fig.update_layout(title='TĂNG TRƯỞNG LỢI NHUẬN', xaxis=dict(title='Năm'),
                          yaxis=dict(title='Lợi nhuận sau thuế  (tỷ VND)', tickformat=',d'),
                          yaxis2=dict(title='Lợi nhuận sau thuế  YoY (%)', overlaying='y', side='right', showgrid=False,
                                      showline=False, zeroline=False),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), barmode='group')
        st.plotly_chart(fig)

        # DOANH THU - LỢI NHUẬN
        result_df['Biên lợi nhuận gộp'] = (result_df['Lợi nhuận gộp về bán hàng và cung cấp dịch vụ'] / result_df[
            'Doanh thu thuần']) * 100
        fig = go.Figure()
        fig.add_trace(
            go.Bar(x=result_df['Năm'], y=result_df['Doanh thu thuần'] / 1e9, name='Doanh thu thuần', yaxis='y1',
                   width=0.4, marker=dict(color='#D2DE32'),
                   hovertemplate='Năm: %{x}<br>Doanh thu thuần: %{y:.4s} tỷ VND<extra></extra>',
                   text=[f"{y:,.2f}" for y in result_df['Doanh thu thuần'] / 1e9], textposition='outside'))
        fig.add_trace(go.Bar(x=result_df['Năm'], y=result_df['Lợi nhuận gộp về bán hàng và cung cấp dịch vụ'] / 1e9,
                             name='Lợi nhuận gộp', yaxis='y1', width=0.4, marker=dict(color='#A3D2E2'),
                             hovertemplate='Năm: %{x}<br>Lợi nhuận gộp: %{y:.4s} tỷ VND<extra></extra>',
                             text=[f"{y:,.2f}" for y in
                                   result_df['Lợi nhuận gộp về bán hàng và cung cấp dịch vụ'] / 1e9],
                             textposition='outside'))
        fig.add_trace(
            go.Scatter(x=result_df['Năm'], y=result_df['Biên lợi nhuận gộp'], name='Biên lợi nhuận gộp', yaxis='y2',
                       hovertemplate='Năm: %{x}<br>Biên lợi nhuận gộp: %{y:.2f}%<extra></extra>',
                       mode='lines+markers+text', line=dict(color='#30B8B8'),
                       text=[f"{y:.2f}%" for y in result_df['Biên lợi nhuận gộp']], textposition='bottom center'))
        fig.update_layout(title='DOANH THU - LỢI NHUẬN', xaxis=dict(title='Năm'),
                          yaxis=dict(title='tỷ VND', tickformat=',d'),
                          yaxis2=dict(title='%', overlaying='y', side='right', showgrid=False, showline=False,
                                      zeroline=False),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), barmode='group')
        st.plotly_chart(fig)

        # TỶ TRỌNG TÀI SẢN
        selected_columns = [
            'TÀI SẢN NGẮN HẠN',
            'TÀI SẢN DÀI HẠN'
        ]
        colors = ['#F9E8D9', '#C1F2B0']
        traces = []
        for i, column in enumerate(selected_columns):
            non_zero_mask = result_df[column].ne(0)
            if non_zero_mask.any():
                total_column = result_df['TỔNG CỘNG TÀI SẢN']
                total_non_zero_mask = total_column.any()
                if total_non_zero_mask:
                    percentage_values = result_df[column] / total_column * 100
                    hover_text = [f"Năm: {year}<br>{column}: {value / 1e9:,.2f} tỷ VND (chiếm {percentage:.2f}%)" for
                                  year, value, percentage in
                                  zip(result_df['Năm'], result_df[column], percentage_values)]
                    trace = go.Bar(x=result_df['Năm'], y=result_df[column] / 1e9, name=column, hovertext=hover_text,
                                   hoverinfo='text', text=[f"{value / 1e9:,.2f}" for value in result_df[column]],
                                   textposition='auto',
                                   textangle=0, width=0.4, marker=dict(color=colors[i]))
                    traces.append(trace)
        layout = go.Layout(title='TỶ TRỌNG TÀI SẢN', xaxis=dict(title='Năm'),
                           yaxis=dict(title='tỷ VND', tickformat=',d'),
                           legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                           barmode='stack')
        fig = go.Figure(data=traces, layout=layout)
        fig.update_layout(height=500)
        st.plotly_chart(fig)

        # TỶ TRỌNG NGUỒN VỐN
        selected_columns = [
            'VỐN CHỦ SỞ HỮU',
            'NỢ PHẢI TRẢ']
        colors = ['#862B0D', '#EE7214']
        traces = []
        for i, column in enumerate(selected_columns):
            non_zero_mask = result_df[column].ne(0)
            if non_zero_mask.any():
                total_column = result_df['TỔNG CỘNG NGUỒN VỐN']
                total_non_zero_mask = total_column.any()
                if total_non_zero_mask:
                    percentage_values = result_df[column] / total_column * 100
                    hover_text = [f"Năm: {year}<br>{column}: {value / 1e9:,.2f} tỷ VND (chiếm {percentage:.2f}%)" for
                                  year, value, percentage in
                                  zip(result_df['Năm'], result_df[column], percentage_values)]
                    trace = go.Bar(x=result_df['Năm'], y=result_df[column] / 1e9, name=column, hovertext=hover_text,
                                   hoverinfo='text', text=[f"{value / 1e9:,.2f}" for value in result_df[column]],
                                   textposition='auto',
                                   textangle=0, width=0.4, marker=dict(color=colors[i]))
                    traces.append(trace)
        layout = go.Layout(title='TỶ TRỌNG NGUỒN VỐN', xaxis=dict(title='Năm'),
                           yaxis=dict(title='tỷ VND', tickformat=',d'),
                           legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                           barmode='stack')
        fig = go.Figure(data=traces, layout=layout)
        fig.update_layout(height=500)
        st.plotly_chart(fig)

        # CƠ CẤU TÀI SẢN
        selected_columns = [
            'Tiền và tương đương tiền (CĐKT)',
            'Đầu tư tài chính ngắn hạn',
            'Đầu tư dài hạn',
            'Các khoản phải thu ngắn hạn',
            'Hàng tồn kho, ròng',
            'Phải thu dài hạn',
            'Tài sản dở dang dài hạn',
            'Tài sản cố định',
            'Tài sản dài hạn khác',
            'Tài sản ngắn hạn khác'
        ]
        colors = ["#862B0D", '#FFC0D9', "#EE7214", "#FF90BC", "#A3D2E2", "#F9F9E0", "#3AA6B9", "#FAC1B8", "#E0F4FF",
                  "#D2DE32"]
        traces = []
        for column, color in zip(selected_columns, colors):
            traces.append(go.Bar(x=result_df['Năm'], y=result_df[column] / 1e9, name=column, width=0.4,
                                 marker=dict(color=color),
                                 hovertemplate='Năm: %{x}<br>%{fullData.name}: %{y:,.2f} tỷ VND<extra></extra>'))
        layout = go.Layout(barmode='stack', title='CƠ CẤU TÀI SẢN', xaxis=dict(title=''),
                           yaxis=dict(title='tỷ VND', tickformat=',.0f'),
                           legend=dict(orientation="h", y=-0.06, x=0), bargap=0.1)
        fig = go.Figure(data=traces, layout=layout)
        fig.update_layout(height=500)
        st.plotly_chart(fig)

        # CƠ CẤU NGUỒN VỐN
        selected_columns = [
            'Phải trả người bán ngắn hạn',
            'Người mua trả tiền trước ngắn hạn',
            'Vay và nợ thuê tài chính ngắn hạn',
            'Vay và nợ thuê tài chính dài hạn',
            'Vốn góp của chủ sở hữu',
            'Thặng dư vốn cổ phần',
            'Lãi chưa phân phối',
            'Lợi ích cổ đông không kiểm soát'
        ]
        colors = ["#FF90BC", "#FFC0D9", "#F9F9E0", "#862B0D", "#3AA6B9", "#E0F4FF", "#D2DE32", "#EE7214"]
        traces = []
        for i, column in enumerate(selected_columns):
            non_zero_mask = result_df[column].ne(0)
            if non_zero_mask.any():
                total_column = result_df['TỔNG CỘNG NGUỒN VỐN']
                total_non_zero_mask = total_column.any()
                if total_non_zero_mask:
                    percentage_values = result_df[column] / total_column * 100
                    hover_text = [f"Năm: {year}<br>{column}: {value / 1e9:.3f} tỷ VND (chiếm {percentage:.2f}%)" for
                                  year, value, percentage in
                                  zip(result_df['Năm'], result_df[column], percentage_values)]
                    trace = go.Bar(
                        x=result_df['Năm'],
                        y=result_df[column] / 1e9,
                        name=column,
                        hovertext=hover_text,
                        hoverinfo='text',
                        width=0.4,
                        marker=dict(color=colors[i])
                    )

                    traces.append(trace)
        layout = go.Layout(barmode='stack', title='CƠ CẤU NGUỒN VỐN', yaxis=dict(title='tỷ VND', tickformat=',.0f'),
                           legend=dict(orientation="h", y=-0.06, x=0), bargap=0.1)
        fig = go.Figure(data=traces, layout=layout)
        fig.update_layout(height=500)
        st.plotly_chart(fig)

        # HIỆU SUẤT SỬ DỤNG TỔNG TÀI SẢN
        result_df['Tổng TS bình quân'] = (result_df['TỔNG CỘNG TÀI SẢN'].shift() + result_df['TỔNG CỘNG TÀI SẢN']) / 2
        result_df['Hiệu suất sử dụng tài sản'] = result_df['Doanh thu thuần'] / result_df['Tổng TS bình quân']
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=result_df['Năm'], y=result_df['Hiệu suất sử dụng tài sản'], name='Hiệu suất sử dụng tài sản',
                       line=dict(color='#30B8B8'),
                       hovertemplate='Năm: %{x}<br>Hiệu suất sử dụng tài sản: %{y:.4s}<extra></extra>',
                       mode='lines+markers+text', text=[f"{y:,.2f}" for y in result_df['Hiệu suất sử dụng tài sản']],
                       textposition='top center'))

        fig.update_layout(
            title='HIỆU SUẤT SỬ DỤNG TỔNG TÀI SẢN',
            xaxis=dict(title='Năm'),
            yaxis=dict(title='', tickformat=',d'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            barmode='group'
        )
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig)

        # HỆ SỐ CƠ CẤU VỐN
        result_df['Tỷ số nợ/TTS'] = (result_df['NỢ PHẢI TRẢ'] / result_df['TỔNG CỘNG TÀI SẢN']) * 100
        result_df['Tỷ số nợ/VCSH'] = (result_df['NỢ PHẢI TRẢ'] / result_df['VỐN CHỦ SỞ HỮU']) * 100
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=result_df['Năm'], y=result_df['Tỷ số nợ/TTS'], mode='lines+markers+text', name='Tỷ số nợ/TTS',
                       hovertemplate='Năm: %{x}<br>Tỷ số nợ/TTS: %{y:.2f}%<extra></extra>',
                       text=[f"{y:.2f}%" for y in result_df['Tỷ số nợ/TTS']], textposition='top center'))
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['Tỷ số nợ/VCSH'], mode='lines+markers+text',
                                 name='Tỷ số nợ/VCSH',
                                 hovertemplate='Năm: %{x}<br>Tỷ số nợ/VCSH: %{y:.2f}%<extra></extra>',
                                 text=[f"{y:.2f}%" for y in result_df['Tỷ số nợ/VCSH']], textposition='top center'))
        fig.update_layout(title='HỆ SỐ CƠ CẤU VỐN', xaxis_title='Năm', yaxis_title='%',
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig)

        # TÍNH THANH KHOẢN
        result_df['Khả năng thanh toán nợ ngắn hạn'] = result_df['TÀI SẢN NGẮN HẠN'] / result_df['Nợ ngắn hạn']
        fig = go.Figure()
        fig.add_trace(
            go.Bar(x=result_df['Năm'], y=result_df['TÀI SẢN NGẮN HẠN'] / 1e9, name='Tài sản ngắn hạn', yaxis='y1',
                   width=0.4, marker=dict(color='#9085BD'),
                   hovertemplate='Năm: %{x}<br>Tài sản ngắn hạn: %{y:.4s} tỷ VND<extra></extra>',
                   text=[f"{y:,.2f}" for y in result_df['TÀI SẢN NGẮN HẠN'] / 1e9], textposition='outside'))
        fig.add_trace(
            go.Bar(x=result_df['Năm'], y=result_df['Nợ ngắn hạn'] / 1e9, name='Nợ ngắn hạn', yaxis='y1', width=0.4,
                   marker=dict(color='#BD85BB'),
                   hovertemplate='Năm: %{x}<br>Nợ ngắn hạn: %{y:.4s} tỷ VND<extra></extra>',
                   text=[f"{y:,.2f}" for y in result_df['Nợ ngắn hạn'] / 1e9], textposition='outside'))
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['Khả năng thanh toán nợ ngắn hạn'],
                                 name='Khả năng thanh toán nợ ngắn hạn', yaxis='y2',
                                 hovertemplate='Năm: %{x}<br>Khả năng thanh toán nợ ngắn hạn: %{y:.2f}%<extra></extra>',
                                 mode='lines+markers+text', line=dict(color='#30B8B8'),
                                 text=[f"{y:.2f}%" for y in result_df['Khả năng thanh toán nợ ngắn hạn']],
                                 textposition='bottom center'))
        fig.update_layout(
            title='TÍNH THANH KHOẢN',
            xaxis=dict(title='Năm'),
            yaxis=dict(title='tỷ VND', tickformat=',d'),
            yaxis2=dict(title=' ', overlaying='y', side='right', showgrid=False, showline=False, zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            barmode='group')
        st.plotly_chart(fig)

        # TỔNG NỢ VAY
        result_df['Tổng nợ vay'] = result_df['Vay và nợ thuê tài chính ngắn hạn'] + result_df[
            'Vay và nợ thuê tài chính dài hạn']
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['Tổng nợ vay'] / 1e9, name='Tổng nợ vay',
                                 line=dict(color='#30B8B8'),
                                 hovertemplate='Năm: %{x}<br>Tổng nợ vay: %{y:.4s} tỷ VND<extra></extra>',
                                 mode='lines+markers+text', text=[f"{y:,.2f}" for y in result_df['Tổng nợ vay'] / 1e9],
                                 textposition='top center'))
        fig.update_layout(
            title='TỔNG NỢ VAY',
            xaxis=dict(title='Năm'),
            yaxis=dict(title='tỷ VND', tickformat=',d'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            barmode='group')
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig)

        # TỶ TRỌNG NỢ VAY
        result_df['Tổng nợ vay'] = result_df['Vay và nợ thuê tài chính ngắn hạn'] + result_df[
            'Vay và nợ thuê tài chính dài hạn']
        result_df['% Nợ/VCSH'] = (result_df['Tổng nợ vay'] / result_df['VỐN CHỦ SỞ HỮU']) * 100
        color_palette = ['#F9E8D9', '#9ADE7B']
        bar_traces = []
        selected_columns = ['Vay và nợ thuê tài chính ngắn hạn', 'Vay và nợ thuê tài chính dài hạn']
        for i, column in enumerate(selected_columns):
            trace = go.Bar(x=result_df['Năm'], y=result_df[column] / 1e9, name=column, hoverinfo='text',
                           hovertext=[f"Năm: {year}<br>{column}: {value / 1e9:.2f} tỷ VND (chiếm {percentage:.2f}%)"
                                      for year, value, percentage in zip(result_df['Năm'], result_df[column],
                                                                         result_df[column] / result_df[
                                                                             'Tổng nợ vay'] * 100)],
                           marker=dict(color=color_palette[i]),
                           text=[f"{value / 1e9:,.2f}" for value in result_df[column]], textposition='auto',
                           textangle=0, width=0.4
                           )
            bar_traces.append(trace)
        line_trace = go.Scatter(x=result_df['Năm'], y=result_df['% Nợ/VCSH'], name='% Nợ/VCSH',
                                yaxis='y2', hovertemplate='Năm: %{x}<br>Nợ vay/VCSH: %{y:.2f}%',
                                line=dict(color='#30B8B8'), text=[f"{y:,.2f}" for y in result_df['% Nợ/VCSH']],
                                textposition='top center')
        layout = go.Layout(barmode='stack', title='TỶ TRỌNG NỢ VAY', xaxis=dict(title='Năm'), yaxis=dict(
            title='tỷ VND', tickformat=',.0f', side='left', automargin=True, ),
                           legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                           yaxis2=dict(title='%', overlaying='y', side='right', showgrid=False, showline=False,
                                       zeroline=False, domain=[0.6, 1], ), margin=dict(r=20, t=60, b=60, l=60),
                           bargap=0.4)
        fig = go.Figure(data=bar_traces + [line_trace], layout=layout)
        fig.update_layout(height=400)
        st.plotly_chart(fig)

        # NỢ VAY VÀ TỶ LỆ D/E
        result_df['D/E'] = result_df['NỢ PHẢI TRẢ'] / result_df['VỐN CHỦ SỞ HỮU']
        fig = go.Figure()
        fig.add_trace(
            go.Bar(x=result_df['Năm'], y=result_df['Nợ ngắn hạn'] / 1e9, name='Nợ ngắn hạn', yaxis='y1', width=0.4,
                   hovertemplate='Năm: %{x}<br>Nợ ngắn hạn: %{y:.4s} tỷ VND<extra></extra>',
                   text=[f"{y:,.2f}" for y in result_df['Nợ ngắn hạn'] / 1e9], textposition='outside'))
        fig.add_trace(
            go.Bar(x=result_df['Năm'], y=result_df['Nợ dài hạn'] / 1e9, name='Nợ dài hạn', yaxis='y1', width=0.4,
                   hovertemplate='Năm: %{x}<br>Nợ dài hạn: %{y:.4s} tỷ VND<extra></extra>',
                   text=[f"{y:,.2f}" for y in result_df['Nợ dài hạn'] / 1e9], textposition='outside'))
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['D/E'], name='D/E', yaxis='y2',
                                 hovertemplate='Năm: %{x}<br>D/E: %{y:.2f}<extra></extra>', mode='lines+markers+text',
                                 text=[f"{y:.2f}" for y in result_df['D/E']], textposition='bottom center'))
        fig.update_layout(title='NỢ VAY VÀ TỶ LỆ D/E', xaxis=dict(title='Năm'),
                          yaxis=dict(title='tỷ VND', tickformat=',d'),
                          yaxis2=dict(title='', overlaying='y', side='right', showgrid=False, showline=False,
                                      zeroline=False),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), barmode='group')
        st.plotly_chart(fig)

        # KIỂM SOÁT HIỆU QUẢ HOẠT ĐỘNG
        result_df['Biên lợi nhuận gộp'] = (result_df['Lợi nhuận gộp về bán hàng và cung cấp dịch vụ'] / result_df[
            'Doanh thu thuần']) * 100
        result_df['EBITDA'] = result_df['Tổng lợi nhuận kế toán trước thuế (KQKD)'] + result_df['Chi phí lãi vay'] + \
                              result_df['Khấu hao TSCĐ']
        result_df['Biên EBITDA'] = (result_df['EBITDA'] / result_df['Doanh thu thuần']) * 100
        result_df['Biên lợi nhuận sau thuế'] = (result_df['Lợi nhuận sau thuế thu nhập doanh nghiệp (KQKD)'] /
                                                result_df['Doanh thu thuần']) * 100
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['Biên lợi nhuận gộp'], name='Biên lợi nhuận gộp',
                                 line=dict(color='#92BD85'),
                                 hovertemplate='Năm: %{x}<br>Biên lợi nhuận gộp: %{y:.2f}%<extra></extra>',
                                 mode='lines+markers+text', text=[f"{y:.2f}%" for y in result_df['Biên lợi nhuận gộp']],
                                 textposition='top center'))
        fig.add_trace(
            go.Scatter(x=result_df['Năm'], y=result_df['Biên lợi nhuận sau thuế'], name='Biên lợi nhuận sau thuế',
                       line=dict(color='#F46A46'),
                       hovertemplate='Năm: %{x}<br>Biên lợi nhuận sau thuế: %{y:.2f}%<extra></extra>',
                       mode='lines+markers+text', text=[f"{y:.2f}%" for y in result_df['Biên lợi nhuận sau thuế']],
                       textposition='top center'))
        fig.add_trace(
            go.Scatter(x=result_df['Năm'], y=result_df['Biên EBITDA'], name='Biên EBITDA', line=dict(color='#F4184C'),
                       hovertemplate='Năm: %{x}<br>Biên EBITDA: %{y:.2f}%<extra></extra>', mode='lines+markers+text',
                       text=[f"{y:.2f}%" for y in result_df['Biên EBITDA']], textposition='top center'))
        fig.update_layout(title='BIÊN LỢI NHUẬN', xaxis=dict(title='Năm'),
                          yaxis=dict(title='%', overlaying='y', side='left', showgrid=False, showline=False,
                                     zeroline=False),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig)

        # ĐÁNH GIÁ TÌNH HÌNH TÀI CHÍNH THÔNG QUA CÁC HỆ SỐ TÀI CHÍNH
        result_df['Hệ số khả năng thanh toán hiện hành'] = (result_df['TỔNG CỘNG TÀI SẢN'] / result_df['NỢ PHẢI TRẢ'])
        result_df['Hệ số khả năng thanh toán ngắn hạn'] = (result_df['TÀI SẢN NGẮN HẠN'] / result_df['Nợ ngắn hạn'])
        result_df['Hệ số khả năng thanh toán tức thời'] = (
                    result_df['Tiền và tương đương tiền (CĐKT)'] / result_df['Nợ ngắn hạn'])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['Hệ số khả năng thanh toán hiện hành'],
                                 name='Hệ số khả năng thanh toán hiện hành', line=dict(color='#EE7214'),
                                 hovertemplate='Năm: %{x}<br>Hệ số khả năng thanh toán hiện hành: %{y:.2f}lần<extra></extra>',
                                 mode='lines+markers+text',
                                 text=[f"{y:.2f}" for y in result_df['Hệ số khả năng thanh toán hiện hành']],
                                 textposition='top center'))
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['Hệ số khả năng thanh toán ngắn hạn'],
                                 name='Hệ số khả năng thanh toán ngắn hạn', line=dict(color='#D2DE32'),
                                 hovertemplate='Năm: %{x}<br>Hệ số khả năng thanh toán ngắn hạn: %{y:.2f}lần<extra></extra>',
                                 mode='lines+markers+text',
                                 text=[f"{y:.2f}" for y in result_df['Hệ số khả năng thanh toán ngắn hạn']],
                                 textposition='bottom center'))
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['Hệ số khả năng thanh toán tức thời'],
                                 name='Hệ số khả năng thanh toán tức thời', line=dict(color='#FF90BC'),
                                 hovertemplate='Năm: %{x}<br>Hệ số khả năng thanh toán tức thời: %{y:.2f}lần<extra></extra>',
                                 mode='lines+markers+text',
                                 text=[f"{y:.2f}" for y in result_df['Hệ số khả năng thanh toán tức thời']],
                                 textposition='top center'))
        fig.update_layout(title='HỆ SỐ KHẢ NĂNG THANH TOÁN', xaxis_title='Năm',
                          yaxis_title='Lần',
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig)

        # CÁC HỆ SỐ VỀ DOANH LỢI
        result_df.columns = result_df.columns.str.strip()
        result_df = result_df.sort_values(by='Năm')
        result_df['VCSH bình quân'] = (result_df['VỐN CHỦ SỞ HỮU'].shift() + result_df['VỐN CHỦ SỞ HỮU']) / 2
        result_df['Tổng Tài sản'] = result_df['TÀI SẢN NGẮN HẠN'] + result_df['TÀI SẢN DÀI HẠN']
        result_df['Tổng TS bình quân'] = (result_df['Tổng Tài sản'].shift() + result_df['Tổng Tài sản']) / 2
        result_df['VCSH bình quân'] = pd.to_numeric(result_df['VCSH bình quân'], errors='coerce')
        result_df['Lợi nhuận sau thuế thu nhập doanh nghiệp'] = pd.to_numeric(
            result_df['Lợi nhuận sau thuế thu nhập doanh nghiệp'], errors='coerce')
        result_df['ROE'] = (result_df['Lợi nhuận sau thuế thu nhập doanh nghiệp (KQKD)'] / result_df[
            'VCSH bình quân']) * 100
        result_df['ROA'] = (result_df['Lợi nhuận sau thuế thu nhập doanh nghiệp (KQKD)'] / result_df[
            'Tổng TS bình quân']) * 100
        result_df['ROS'] = (result_df['Lợi nhuận sau thuế thu nhập doanh nghiệp (KQKD)'] / result_df[
            'Doanh thu thuần']) * 100
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['ROE'], name='ROE', line=dict(color='#B830B3'),
                                 hovertemplate='Năm: %{x}<br>ROE: %{y:.2f}%<extra></extra>', mode='lines+markers+text',
                                 text=[f"{y:.2f}%" for y in result_df['ROE']], textposition='top center'))
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['ROA'], name='ROA', line=dict(color='#30B8B8'),
                                 hovertemplate='Năm: %{x}<br>ROA: %{y:.2f}%<extra></extra>', mode='lines+markers+text',
                                 text=[f"{y:.2f}%" for y in result_df['ROA']], textposition='top center'))
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['ROS'], name='ROS', line=dict(color='#30B852'),
                                 hovertemplate='Năm: %{x}<br>ROS: %{y:.2f}%<extra></extra>', mode='lines+markers+text',
                                 text=[f"{y:.2f}%" for y in result_df['ROS']], textposition='top center'))
        fig.update_layout(title='TỶ SỐ SINH LỜI', xaxis_title='Năm',
                          yaxis=dict(title='%', overlaying='y', side='left', showgrid=False, showline=False,
                                     zeroline=False),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig)

        # VỐN LƯU ĐỘNG RÒNG
        result_df['Vốn lưu động ròng'] = result_df['TÀI SẢN NGẮN HẠN'] - result_df['Nợ ngắn hạn']
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['Vốn lưu động ròng'] / 1e9, name='Vốn lưu động ròng',
                                 line=dict(color='#9085BD'),
                                 hovertemplate='Năm: %{x}<br>Vốn lưu động ròng: %{y:.4s} tỷ VND<extra></extra>',
                                 mode='lines+markers+text',
                                 text=[f"{y:,.2f}" for y in result_df['Vốn lưu động ròng'] / 1e9],
                                 textposition='top center'))
        fig.update_layout(title='VỐN LƯU ĐỘNG RÒNG', xaxis=dict(title='Năm'),
                          yaxis=dict(title='tỷ VND', tickformat=',d'),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), barmode='group')
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig)

        # KHẢ NĂNG TRẢ NỢ
        result_df['EBIT'] = result_df['Tổng lợi nhuận kế toán trước thuế (KQKD)'] + abs(result_df['Chi phí lãi vay'])
        result_df['EBITDA'] = result_df['Tổng lợi nhuận kế toán trước thuế (KQKD)'] + abs(
            result_df['Chi phí lãi vay']) + result_df['Khấu hao TSCĐ']
        result_df['Hệ số khả năng thanh toán hiện hành'] = (result_df['TỔNG CỘNG TÀI SẢN'] / result_df['NỢ PHẢI TRẢ'])
        result_df['EBIT/Lãi vay'] = result_df['EBIT'] / abs(result_df['Chi phí lãi vay'])
        result_df['Tổng nợ vay'] = result_df['Vay và nợ thuê tài chính ngắn hạn'] + result_df[
            'Vay và nợ thuê tài chính dài hạn']
        result_df['Nợ vay/EBITDA'] = result_df['Tổng nợ vay'] / result_df['EBITDA']
        fig = go.Figure()
        fig.add_trace(go.Bar(x=result_df['Năm'], y=result_df['Hệ số khả năng thanh toán hiện hành'],
                             name='Hệ số khả năng thanh toán hiện hành', marker=dict(color='#EE7214'), yaxis='y1',
                             width=0.4,
                             hovertemplate='Năm: %{x}<br>Hệ số khả năng thanh toán hiện hành: %{y:.2f}<extra></extra>',
                             text=[f"{y:.2f}" for y in result_df['Hệ số khả năng thanh toán hiện hành']],
                             textposition='outside'))
        fig.add_trace(
            go.Scatter(x=result_df['Năm'], y=result_df['EBIT/Lãi vay'], name='EBIT/Lãi vay', line=dict(color='#B830B3'),
                       yaxis='y2',
                       hovertemplate='Năm: %{x}<br>EBIT/Lãi vay: %{y:.2f}<extra></extra>', mode='lines+markers+text',
                       text=[f"{y:.2f}" for y in result_df['EBIT/Lãi vay']], textposition='top center'))
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['Nợ vay/EBITDA'], name='Nợ vay/EBITDA',
                                 line=dict(color='#30B8B8'), yaxis='y2',
                                 hovertemplate='Năm: %{x}<br>Nợ vay/EBITDA: %{y:.2f}<extra></extra>',
                                 mode='lines+markers+text', text=[f"{y:.2f}" for y in result_df['Nợ vay/EBITDA']],
                                 textposition='top center'))
        fig.update_layout(title='KHẢ NĂNG TRẢ NỢ', xaxis=dict(title='Năm'),
                          yaxis=dict(title='Lần', tickformat=',d', tickvals=list(range(1, len(result_df) + 1))),
                          yaxis2=dict(title='Lần', overlaying='y', side='right', showgrid=False, showline=False,
                                      zeroline=False),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), barmode='group')
        st.plotly_chart(fig)

        # EPS
        result_df['Tỷ lệ tăng trưởng EPS'] = ((result_df['Lãi cơ bản trên cổ phiếu'] - result_df[
            'Lãi cơ bản trên cổ phiếu'].shift(1)) / result_df['Lãi cơ bản trên cổ phiếu'].shift(1)) * 100
        fig = go.Figure()
        fig.add_trace(go.Bar(x=result_df['Năm'], y=result_df['Lãi cơ bản trên cổ phiếu'], name='EPS', yaxis='y1',
                             marker=dict(color='#4FC0D0'), width=0.4,
                             hovertemplate='Năm: %{x}<br>EPS: %{y:.2f} VND<extra></extra>',
                             text=[f"{y:,.2f}" for y in result_df['Lãi cơ bản trên cổ phiếu']], textposition='outside'))

        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['Tỷ lệ tăng trưởng EPS'], name='Tỷ lệ tăng trưởng EPS',
                                 yaxis='y2',line=dict(color='#EE7214'),
                                 hovertemplate='Năm: %{x}<br>Tỷ lệ tăng trưởng EPS: %{y:.2f}<extra></extra>',
                                 mode='lines+markers+text',
                                 text=[f"{y:.2f}" for y in result_df['Tỷ lệ tăng trưởng EPS']],
                                 textposition='bottom center'))
        fig.update_layout(
            title='Tỷ lệ tăng trưởng EPS',
            xaxis=dict(title='Năm'),
            yaxis=dict(title='VND', tickformat=',d'),
            yaxis2=dict(title='', overlaying='y', side='right', showgrid=False, showline=False, zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            barmode='group')
        st.plotly_chart(fig)

        # DÒNG TIỀN
        traces = []
        selected_columns = ["Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh (TT)",
                            "Lưu chuyển tiền tệ ròng từ hoạt động đầu tư (TT)",
                            "Lưu chuyển tiền tệ từ hoạt động tài chính (TT)"]
        selected_columns_df = result_df[selected_columns]
        selected_columns_df = selected_columns_df.apply(pd.to_numeric, errors='coerce').astype('Int64')
        colors = ['#F9E8D9', '#C1F2B0', '#F9F9E0']
        traces = []
        for column in selected_columns_df.columns:
            if selected_columns_df[column].ne(0).any():
                hover_text = [f"Năm: {year}<br>{column}: {value / 1e9:,.3f} tỷ" for year, value in
                              zip(result_df['Năm'], selected_columns_df[column])]
                trace = go.Bar(x=result_df['Năm'], y=selected_columns_df[column] / 1e9, name=column,
                               hovertext=hover_text, hoverinfo='text',
                               text=[f"{value / 1e9:,.2f}" for value in result_df[column]], textposition='auto',
                               textangle=0, width=0.4)
                traces.append(trace)
        money_trace = go.Scatter(x=result_df['Năm'], y=result_df['Tiền và tương đương tiền cuối kỳ (TT)'] / 1e9,
                                 mode='lines', name='Tiền và tương đương tiền cuối kỳ',
                                 hovertemplate='Năm: %{x}<br> Tiền và tương đương tiền cuối kỳ: %{y:,.2f} tỷ VND<extra></extra>',
                                 )
        traces.append(money_trace)
        layout = go.Layout(barmode='relative', title='LƯU CHUYỂN TIỀN TỆ', legend=dict(orientation="h", y=-0.06, x=0),
                           bargap=0.3, xaxis=dict(zeroline=False, zerolinewidth=0),
                           yaxis=dict(tickformat=",.0f", title="tỷ VND"), height=500)
        fig = go.Figure(data=traces, layout=layout)
        st.plotly_chart(fig)

        # PHÂN TÍCH DUPONT
        result_df['Tổng TS bình quân'] = (result_df['Tổng Tài sản'].shift() + result_df['Tổng Tài sản']) / 2
        result_df['Biên lợi nhuận ròng'] = (result_df['Lợi nhuận sau thuế thu nhập doanh nghiệp (KQKD)'] / result_df[
            'Doanh thu thuần']) * 100
        result_df['Vòng quay tài sản'] = (result_df['Doanh thu thuần'] / result_df['Tổng TS bình quân'])
        result_df['VCSH bình quân'] = (result_df['VỐN CHỦ SỞ HỮU'].shift() + result_df['VỐN CHỦ SỞ HỮU']) / 2
        result_df['Đòn bẩy tài chính'] = result_df['TỔNG CỘNG TÀI SẢN'] / result_df['VCSH bình quân']
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=result_df['Năm'], y=result_df['ROE'], name='ROE',
                             hovertemplate='Năm: %{x}<br>ROE: %{y:.2f}%<extra></extra>', marker=dict(color='#0C8435'),
                             text=[f"{y:.2f}" for y in result_df['ROE']], textposition='outside'))
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['Biên lợi nhuận ròng'], mode='lines+markers',
                                 name='Biên lợi nhuận ròng', line=dict(color='#B830B3'),
                                 hovertemplate='Năm: %{x}<br>Biên lợi nhuận ròng: %{y:.2f}%<extra></extra>'))
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['Vòng quay tài sản'], mode='lines+markers',
                                 name='Vòng quay tài sản',
                                 line=dict(color='#30B8B8'),
                                 hovertemplate='Năm: %{x}<br>Vòng quay tài sản: %{y:.2f}lần<extra></extra>'),
                      secondary_y=True)
        fig.add_trace(go.Scatter(x=result_df['Năm'], y=result_df['Đòn bẩy tài chính'], mode='lines+markers',
                                 name='Đòn bẩy tài chính',
                                 line=dict(color='#EE7214'),
                                 hovertemplate='Năm: %{x}<br>Đòn bẩy tài chính: %{y:.2f}<extra></extra>'),
                      secondary_y=True)
        fig.update_layout(title='PHÂN TÍCH DUPONT', xaxis_title='Năm', yaxis_title='%',
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                          legend_title_font=dict(size=14), bargap=0.5)
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        fig.update_yaxes(title_text="Lần", secondary_y=True, showgrid=False)
        st.plotly_chart(fig)



        # Logic cho phân tích ngành
elif selected == "Phân tích ngành":
    st.header("**PHÂN TÍCH NGÀNH**")
    def clean_data(file_path):
        df = pd.read_excel(file_path)
        df = df.iloc[7:, :]
        df.columns = df.iloc[0]
        df.columns.name = None
        df = df.iloc[1:, :]
        df.reset_index(drop=True, inplace=True)
        new_column_names = [col.split('\n')[0] for col in df.columns]
        df.columns = new_column_names
        index_to_keep = df[df['STT'] == 1664].index[0]
        df = df.loc[:index_to_keep]
        return df
    def load_and_display_data(dfs, industry_code, report_tables):
        stock_data = pd.DataFrame()
        for df_name, df in dfs.items():
            important_columns = [col for col in df.columns for table in report_tables if col.startswith(table + '.')]
            stock_year_data = df[df['Ngành ICB - cấp 3'] == industry_code]
            stock_year_data = stock_year_data[
                ['Năm', 'Mã', 'Tên công ty', 'Sàn', 'Ngành ICB - cấp 3'] + important_columns]
            stock_year_data = stock_year_data.loc[:, ~stock_year_data.columns.duplicated()]
            stock_data = pd.concat([stock_data, stock_year_data])
        stock_data['Năm'] = stock_data['Năm'].astype('Int64')
        stock_data = stock_data[stock_data['Sàn'] != 'UPCoM']
        stock_data.sort_values(by='Năm', inplace=True)
        stock_data.reset_index(drop=True, inplace=True)
        return stock_data
    def display_stock_data(industry_code):
        report_tables = ['CĐKT', 'KQKD', 'LCTT', 'TM', 'BCTCKH']
        result_data = load_and_display_data(dfs, industry_code, report_tables)
        return result_data
    file_paths = ["C:/Users/admin/GPM1_ck/data/2022-Vietnam.xlsx",
                  "C:/Users/admin/GPM1_ck/data/2021-Vietnam.xlsx",
                  "C:/Users/admin/GPM1_ck/data/2020-Vietnam.xlsx",
                  "C:/Users/admin/GPM1_ck/data/2019-Vietnam.xlsx",
                  "C:/Users/admin/GPM1_ck/data/2018-Vietnam.xlsx"]
    dfs = {}
    for file_path in file_paths:
        year = file_path.split('/')[-1].split('-')[0]
        dfs[f"df_{year}"] = clean_data(file_path)
    industry_code_to_display = 'Bán lẻ'
    df = display_stock_data(industry_code_to_display)
    df = df.rename(columns={
        'KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp': 'Lợi nhuận sau thuế thu nhập doanh nghiệp (KQKD)',
        'KQKD. Tổng lợi nhuận kế toán trước thuế': 'Tổng lợi nhuận kế toán trước thuế (KQKD)',
        'KQKD. Trong đó: Chi phí lãi vay': 'Chi phí lãi vay',
        'CĐKT. Tiền và tương đương tiền ': 'Tiền và tương đương tiền (CĐKT)'
    })
    new_columns = [col.split('.')[-1] for col in df.columns]
    df.rename(columns=dict(zip(df.columns, new_columns)), inplace=True)
    result_df = df.copy()
    result_df.columns = result_df.columns.str.strip()
    if 'current_tab_nganh' not in st.session_state:
        st.session_state['current_tab_nganh'] = 'Tổng quan ngành'
    col1, spacer1, col2, spacer2, col3, spacer3, col4, spacer4, col5 = st.columns([1, 0.25, 1, 0.25, 1, 0.25, 1, 0.25, 1])
    with col1:
        option_tong_quan = st.button("Tổng quan ngành")
    with col2:
        option_chi_so = st.button("Số liệu tài chính")
    with col3:
        option_bieu_do = st.button("Biểu đồ tài chính")
    with col4:
        option_treemap = st.button("Treemap chart")
    with col5:
        option_bubble_chart = st.button("Bubble chart")
    if option_tong_quan:
        st.session_state['current_tab_nganh'] = 'Tổng quan ngành'
    elif option_chi_so:
        st.session_state['current_tab_nganh'] = 'Số liệu tài chính'
    elif option_bieu_do:
        st.session_state['current_tab_nganh'] = 'Biểu đồ tài chính'
    elif option_treemap:
        st.session_state['current_tab_nganh'] = 'Treemap chart'
    elif option_bubble_chart:
        st.session_state['current_tab_nganh'] = 'Bubble chart'
    st.write("\n"
             "\n")

    if st.session_state['current_tab_nganh'] == 'Tổng quan ngành':
        st.markdown(
            "<p style='text-align: justify;'>"
            "Ngành bán lẻ là ngành rất rộng, chia ra nhiều mảng, nên có sự phức tạp và khó nắm bắt hết toàn bộ một cách sâu rộng. "
            "Song cũng nhờ đó mà có nhiều cơ hội cho người nào nhìn ra bức tranh ẩn sau nó. "
            "Điểm chung và cũng là ưu điểm của các hãng bán lẻ là mô hình kinh doanh ít phụ thuộc B2B – có phải thu và công nợ lớn, "
            "mà chủ yếu đầu ra là khách hàng cá nhân – có đặc tính bán và thu tiền ngay cho nên giảm thiểu tối đa rủi ro phải thu, nợ xấu. "
            "Như vậy, khi phân tích cổ phiếu thuộc ngành bán lẻ, chúng ta cần phân loại ngay từ đầu một cách chính xác để nắm rõ ưu nhược "
            "điểm cũng như đặc tính riêng của từng mảng, qua đó có cách định giá hợp lý hơn."
            "</p>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align: justify;'>"
            "Hiện nay người ta sẽ phân loại mảng tương ứng với tính chất của các mặt hàng như hàng lâu bền, bách hóa… "
            "Theo đó, cách quản lý vận hành chuỗi hàng bán lẻ và sức cạnh tranh cũng khác nhau. Do đặc thù phân mảnh ở "
            "các lĩnh vực bán lẻ như vậy nên gây nhiều khó khăn cho các nhà kinh doanh và nhà đầu tư. "
            "Đánh giá, mặc dù cơ hội trong tương lai có nhiều nhưng chưa xảy ra rõ rệt ở Việt Nam do nền kinh tế đang phát triển và quy mô "
            "tầm nhỏ, phụ thuộc vào nước ngoài bởi họ có nhiều kinh nghiệm hơn chúng ta trong các mảng này."
            "</p>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align: justify;'>"
            "Ngành bán lẻ có triển vọng rất tích cực bởi kinh tế Việt Nam giai đoạn 2019-2022 giữ vững mức tăng trưởng "
            "bình quân trên 6.5%/năm. Xu hướng đô thị hóa và đông đảo dân số trẻ (50 triệu người), xu hướng FDI giúp gia "
            "tăng tỷ lệ việc làm. Từ đó tạo ra nhiều lĩnh vực dịch vụ bán lẻ mới mẻ, rộng mở."
            "</p>",
            unsafe_allow_html=True
        )


    elif st.session_state['current_tab_nganh'] == 'Số liệu tài chính':
        stock_data = display_stock_data('Bán lẻ')
        stock_data['Năm'] = stock_data['Năm'].astype(str)
        stock_data['Năm'] = stock_data['Năm'].str.replace(',', '').astype(int)
        cdk_columns = [col for col in stock_data.columns if col.startswith('CĐKT.')]
        if cdk_columns:
            st.write("### Cân đối kế toán")
        st.dataframe(stock_data[['Năm', 'Mã', 'Tên công ty', 'Sàn', 'Ngành ICB - cấp 3'] + cdk_columns])
        kqkd_columns = [col for col in stock_data.columns if col.startswith('KQKD.')]
        if kqkd_columns:
            st.write("### Kết quả kinh doanh")
        st.dataframe(stock_data[['Năm', 'Mã', 'Tên công ty', 'Sàn', 'Ngành ICB - cấp 3'] + kqkd_columns])
        lctt_columns = [col for col in stock_data.columns if col.startswith('LCTT.')]
        if lctt_columns:
            st.write("### Lưu chuyển tiền tệ")
        st.dataframe(stock_data[['Năm', 'Mã', 'Tên công ty', 'Sàn', 'Ngành ICB - cấp 3'] + lctt_columns])
        tm_columns = [col for col in stock_data.columns if col.startswith('TM.')]
        if tm_columns:
            st.write("### Thuyết minh")
        st.dataframe(stock_data[['Năm', 'Mã', 'Tên công ty', 'Sàn', 'Ngành ICB - cấp 3'] + tm_columns])

    elif st.session_state['current_tab_nganh'] == 'Biểu đồ tài chính':
        # TOP 10 DOANH NGHIỆP CÓ ROE CAO NHẤT NĂM 2022
        result_df_2022 = result_df[result_df['Năm'] == 2022]
        result_df_2021 = result_df[result_df['Năm'] == 2021]
        result_df_combined = result_df_2022.set_index('Mã').join(result_df_2021.set_index('Mã'), rsuffix='_2021')
        result_df_combined['VCSH bình quân'] = (result_df_combined['VỐN CHỦ SỞ HỮU_2021'] + result_df_combined[
            'VỐN CHỦ SỞ HỮU']) / 2
        result_df_combined['ROE'] = (result_df_combined['Lợi nhuận sau thuế thu nhập doanh nghiệp (KQKD)'] /
                                     result_df_combined['VCSH bình quân']) * 100
        result_df_combined['ROE'] = pd.to_numeric(result_df_combined['ROE'], errors='coerce').fillna(0)
        top_10_roe_companies_2022 = result_df_combined.nlargest(10, 'ROE')
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top_10_roe_companies_2022.index,
            y=top_10_roe_companies_2022['ROE'],
            text=[f"{roe:.2f}%" for roe in top_10_roe_companies_2022['ROE']],
            textposition='outside',
            marker=dict(color='#FFA07A')))
        fig.update_layout(
            title='TOP 10 DOANH NGHIỆP CÓ ROE CAO NHẤT NĂM 2022',
            xaxis=dict(title='Mã doanh nghiệp'),
            yaxis=dict(title='ROE (%)', tickformat='.2f'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig)


        # DOANH THU - LỢI NHUẬN
        grouped_df = result_df.groupby('Năm').agg(
            {'Doanh thu thuần': 'sum', 'Lợi nhuận gộp về bán hàng và cung cấp dịch vụ': 'sum'}).reset_index()
        fig = go.Figure()
        fig.add_trace(
            go.Bar(x=grouped_df['Năm'], y=grouped_df['Doanh thu thuần'] / 1e9, name='Doanh thu thuần', yaxis='y1',
                   width=0.4, marker=dict(color='#4FC0D0'),
                   hovertemplate='Năm: %{x}<br>Doanh thu thuần: %{y:.4s} tỷ VNĐ<extra></extra>',
                   text=[f"{y:,.2f}" for y in grouped_df['Doanh thu thuần'] / 1e9], textposition='outside'))
        fig.add_trace(
            go.Scatter(x=grouped_df['Năm'], y=grouped_df['Lợi nhuận gộp về bán hàng và cung cấp dịch vụ'] / 1e9,
                       name='Lợi nhuận gộp',
                       yaxis='y2', line=dict(color='#862B0D'),
                       hovertemplate='Năm: %{x}<br>Lợi nhuận gộp: %{y:.2f}%<extra></extra>', mode='lines+markers+text',
                       text=[f"{y:,.2f}" for y in grouped_df['Lợi nhuận gộp về bán hàng và cung cấp dịch vụ'] / 1e9],
                       textposition='bottom center'))
        fig.update_layout(
            title='DOANH THU - LỢI NHUẬN', xaxis=dict(title='Năm'), yaxis=dict(title='tỷ VNĐ', tickformat=',d'),
            yaxis2=dict(title='tỷ VNĐ', overlaying='y', side='right', showgrid=False, showline=False, zeroline=False,
                        tickformat=',d'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            barmode='group')
        st.plotly_chart(fig)

        # TỔNG NỢ/TỔNG VỐN CHỦ SỞ HỮU CỦA NGÀNH
        grouped_df = result_df.groupby('Năm').agg({'NỢ PHẢI TRẢ': 'sum', 'VỐN CHỦ SỞ HỮU': 'sum'}).reset_index()
        grouped_df['Tổng nợ/Tổng VCSH'] = grouped_df['NỢ PHẢI TRẢ'] / grouped_df['VỐN CHỦ SỞ HỮU']
        fig = go.Figure()
        fig.add_trace(
            go.Bar(x=grouped_df['Năm'], y=grouped_df['NỢ PHẢI TRẢ'] / 1e9, name='Tổng nợ phải trả', yaxis='y1',
                   width=0.4, marker=dict(color='#F46A46'),
                   hovertemplate='Năm: %{x}<br>Tổng nợ phải trả: %{y:.4s} tỷ VNĐ<extra></extra>',
                   text=[f"{y:,.2f}" for y in grouped_df['NỢ PHẢI TRẢ'] / 1e9], textposition='outside'))
        fig.add_trace(
            go.Scatter(x=grouped_df['Năm'], y=grouped_df['Tổng nợ/Tổng VCSH'], name='Tổng nợ/Tổng VCSH', yaxis='y2',
                       line=dict(color='#92BD85'),
                       hovertemplate='Năm: %{x}<br>Tổng nợ/Tổng VCSH: %{y:.2f}<extra></extra>',
                       mode='lines+markers+text',
                       text=[f"{y:.2f}" for y in grouped_df['Tổng nợ/Tổng VCSH']], textposition='bottom center'))
        fig.update_layout(
            title='TỔNG NỢ/TỔNG VỐN CHỦ SỞ HỮU CỦA NGÀNH', xaxis=dict(title='Năm'),
            yaxis=dict(title='tỷ VNĐ', tickformat=',d'),
            yaxis2=dict(title='', overlaying='y', side='right', showgrid=False, showline=False, zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            barmode='group')
        st.plotly_chart(fig)

        # VÒNG QUAY TÀI SẢN
        result_df['Tổng Tài sản'] = result_df['TÀI SẢN NGẮN HẠN'] + result_df['TÀI SẢN DÀI HẠN']
        result_df['Tổng TS bình quân'] = (result_df['Tổng Tài sản'].shift() + result_df['Tổng Tài sản']) / 2
        grouped_df = result_df.groupby('Năm').agg({'Doanh thu thuần': 'sum', 'Tổng TS bình quân': 'sum'}).reset_index()
        grouped_df['Vòng quay tài sản'] = (grouped_df['Doanh thu thuần'] / grouped_df['Tổng TS bình quân'])
        fig = go.Figure()
        fig.add_trace(
            go.Bar(x=grouped_df['Năm'], y=grouped_df['Vòng quay tài sản'], name='Vòng quay tài sản', width=0.4,
                   marker=dict(color='#9085BD'),
                   hovertemplate='Năm: %{x}<br>Vòng quay tài sản: %{y:.4s} <extra></extra>',
                   text=[f"{y:,.2f}" for y in grouped_df['Vòng quay tài sản']], textposition='outside'))
        fig.update_layout(
            title='VÒNG QUAY TÀI SẢN', xaxis=dict(title='Năm'),
            yaxis=dict(title='', tickformat=',d', tickvals=list(range(1, len(result_df) + 1))),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            barmode='group')
        st.plotly_chart(fig)

        #BIỂU ĐỒ EBITDA/NỢ NGẮN HẠN VÀ HỆ SỐ THANH TOÁN HIỆN HÀNH NĂM 2022
        result_df_2022 = result_df[result_df['Năm'] == 2022]
        result_df_2022['EBITDA'] = result_df_2022['Tổng lợi nhuận kế toán trước thuế (KQKD)'] + result_df_2022[
            'Chi phí lãi vay'] + result_df_2022['Khấu hao TSCĐ']
        result_df_2022['EBITDA/Nợ ngắn hạn'] = result_df_2022['EBITDA'] / result_df_2022['Nợ ngắn hạn']
        result_df_2022['Hệ số thanh toán hiện hành'] = result_df_2022['TÀI SẢN NGẮN HẠN'] / result_df_2022[
            'Nợ ngắn hạn']
        fig = go.Figure()
        fig.add_trace(go.Bar(x=result_df_2022['Mã'], y=result_df_2022['EBITDA/Nợ ngắn hạn'], name='EBITDA/Nợ ngắn hạn',
                             yaxis='y', marker=dict(color='#4FC0D0'), width=0.4, customdata=result_df_2022['Năm'],
                             hovertemplate='Năm: 2022<br>Mã: %{x}<br>EBITDA/Nợ ngắn hạn: %{y:.2f} lần<extra></extra>'))
        fig.add_trace(go.Bar(x=result_df_2022['Mã'], y=result_df_2022['Hệ số thanh toán hiện hành'],
                             name='Hệ số thanh toán hiện hành',
                             yaxis='y', marker=dict(color='#92BD85'), width=0.4, customdata=result_df_2022['Năm'],
                             hovertemplate='Năm: 2022<br>Mã: %{x}<br>Hệ số thanh toán hiện hành: %{y:.2f} lần<extra></extra>'))
        fig.update_layout(title='Biểu đồ Hệ số thanh toán hiện hành năm 2022', xaxis=dict(title='Mã công ty'),
                          yaxis=dict(title='Hệ số thanh toán hiện hành', overlaying='y', side='left', showgrid=False,
                                     showline=False, zeroline=False),
                          legend=dict(orientation="h", y=-0.06, x=1), barmode='group')
        fig.update_layout(title='BIỂU ĐỒ EBITDA/NỢ NGẮN HẠN VÀ HỆ SỐ THANH TOÁN HIỆN HÀNH NĂM 2022', xaxis=dict(title='Mã doanh nghiệp'),
                          yaxis=dict(title='Lần', tickformat=',d'),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), barmode='group')
        st.plotly_chart(fig)

        # SO SÁNH DOANH THU MWG VỚI DOANH THU TRUNG BÌNH NGÀNH
        mwg_data = result_df[result_df['Mã'] == 'MWG']
        mwg_data = mwg_data.sort_values(by='Năm')
        avg_nganh_revenue = result_df.groupby('Năm')['Doanh thu thuần'].mean().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=mwg_data['Năm'],
            y=mwg_data['Doanh thu thuần'] / 1e9,
            mode='lines+markers',
            name='Doanh thu của MWG', line=dict(color='#92BD85'),
            hovertemplate='Năm: %{x}<br>Doanh thu MWG: %{y:,.2f} tỷ VND<extra></extra>'
        ))
        fig.add_trace(go.Scatter(
            x=avg_nganh_revenue['Năm'],
            y=avg_nganh_revenue['Doanh thu thuần'] / 1e9,
            mode='lines+markers',
            name=f'Doanh thu trung bình của ngành Bán lẻ', line=dict(color='#F46A46'),
            hovertemplate='Năm: %{x}<br>Doanh thu trung bình ngành: %{y:,.2f} tỷ VND<extra></extra>'
        ))

        fig.update_layout(title='SO SÁNH DOANH THU MWG VỚI DOANH THU TRUNG BÌNH NGÀNH', xaxis=dict(title='Năm'),
                          yaxis=dict(title='tỷ VNĐ', overlaying='y', side='left', showgrid=False, showline=False,
                                     zeroline=False),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig)

    elif st.session_state['current_tab_nganh'] == 'Treemap chart':

        # DOANH THU THUẦN CỦA CÁC DOANH NGHIỆP TRONG NGÀNH BÁN LẺ NĂM 2022
        result_df_2022 = result_df[result_df['Năm'] == 2022]
        result_df_2022['Doanh thu thuần'] /= 1e9
        color_continuous_midpoint = np.average(result_df_2022['Doanh thu thuần'])
        fig = px.treemap(result_df_2022, path=['Ngành ICB - cấp 3', 'Mã'],
                         values='Doanh thu thuần',
                         color='Doanh thu thuần',
                         hover_data=['Mã', 'Doanh thu thuần'],
                         color_continuous_scale='RdBu',
                         color_continuous_midpoint=color_continuous_midpoint,
                         title=f'DOANH THU THUẦN CỦA CÁC DOANH NGHIỆP TRONG NGÀNH NĂM 2022')
        fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
        fig.update_layout(coloraxis_colorbar=dict(title='Doanh thu thuần', tickformat=",.2f", ticksuffix=' tỷ VND'))
        st.plotly_chart(fig)

        # LỢI NHUẬN GỘP CỦA CÁC DOANH NGHIỆP TRONG NGÀNH BÁN LẺ NĂM 2022
        result_df_2022 = result_df[result_df['Năm'] == 2022]
        result_df_2022['Lợi nhuận gộp về bán hàng và cung cấp dịch vụ'] /= 1e9
        color_continuous_midpoint = np.average(result_df_2022['Lợi nhuận gộp về bán hàng và cung cấp dịch vụ'])
        fig = px.treemap(result_df_2022, path=['Ngành ICB - cấp 3', 'Mã'],
                         values='Lợi nhuận gộp về bán hàng và cung cấp dịch vụ',
                         color='Lợi nhuận gộp về bán hàng và cung cấp dịch vụ',
                         hover_data=['Mã', 'Lợi nhuận gộp về bán hàng và cung cấp dịch vụ'],
                         color_continuous_scale='RdBu',
                         color_continuous_midpoint=color_continuous_midpoint,
                         title=f'LỢI NHUẬN GỘP CỦA CÁC DOANH NGHIỆP TRONG NGÀNH NĂM 2022')
        fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig)

    elif st.session_state['current_tab_nganh'] == 'Bubble chart':
        # SO SÁNH TỔNG TÀI SẢN CỦA MWG VỚI NGÀNH BÁN LẺ
        result_df_2022 = result_df[result_df['Năm'] == 2022]
        result_df_2022['Size'] = result_df_2022['TỔNG CỘNG TÀI SẢN'] / result_df_2022['TỔNG CỘNG TÀI SẢN'].max() * 100
        result_df_2022['Size'] = pd.to_numeric(result_df_2022['Size'], errors='coerce').fillna(0)
        mwg_color = '#FFA500'
        fig = go.Figure()
        for index, row in result_df_2022.iterrows():
            color = mwg_color if row['Mã'] == 'MWG' else '#4FC0D0'
            fig.add_trace(go.Scatter(
                x=[row['Mã']],
                y=[row['TỔNG CỘNG TÀI SẢN'] / 1e9],
                mode='markers',
                marker=dict(size=row['Size'], sizemode='diameter', color=color, opacity=0.7,
                            line=dict(color='DarkSlateGrey', width=2)), text=row['Mã'],
                hovertemplate='Mã: %{x}<br>Tổng tài sản: %{y:,.2f} tỷ VND<extra></extra>'))
        fig.update_layout(
            title='SO SÁNH TỔNG TÀI SẢN CỦA MWG VỚI NGÀNH BÁN LẺ NĂM 2022',
            xaxis=dict(title='Mã doanh nghiệp'),
            yaxis=dict(title='tỷ VND', tickformat=',d'),
            showlegend=False)
        st.plotly_chart(fig)

        # SO SÁNH VỐN CHỦ SỞ HỮU CỦA MWG VỚI NGÀNH BÁN LẺ
        result_df_2022 = result_df[result_df['Năm'] == 2022]
        result_df_2022['Size'] = result_df_2022['VỐN CHỦ SỞ HỮU'] / result_df_2022['VỐN CHỦ SỞ HỮU'].max() * 100
        result_df_2022['Size'] = pd.to_numeric(result_df_2022['Size'], errors='coerce').fillna(0)
        mwg_color = '#F9F9E0'
        fig = go.Figure()
        for index, row in result_df_2022.iterrows():
            color = mwg_color if row['Mã'] == 'MWG' else '#9085BD'
            fig.add_trace(go.Scatter(
                x=[row['Mã']],
                y=[row['VỐN CHỦ SỞ HỮU'] / 1e9],
                mode='markers',
                marker=dict(size=row['Size'], sizemode='diameter', color=color, opacity=0.7,
                            line=dict(color='DarkSlateGrey', width=2)),
                text=row['Mã'], hovertemplate='Mã: %{x}<br>Vốn chủ sở hữu: %{y:,.2f} tỷ VND<extra></extra>'))
        fig.update_layout(
            title='SO SÁNH VỐN CHỦ SỞ HỮU CỦA MWG VỚI NGÀNH BÁN LẺ NĂM 2022',
            xaxis=dict(title='Mã doanh nghiệp'),
            yaxis=dict(title='tỷ VND', tickformat=',d'),
            showlegend=False)
        st.plotly_chart(fig)









