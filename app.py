
import requests
import pandas as pd
import plotly.express as px
import streamlit as st
import time

st.set_page_config(page_title="Crypto Liquidity Monitor", layout="wide")
st.title("📊 实时加密货币挂单热力图监控")

symbol = st.selectbox("选择币种:", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])
limit = st.slider("显示深度档数:", min_value=10, max_value=500, value=100, step=10)
refresh_interval = st.slider("刷新间隔 (秒):", min_value=5, max_value=60, value=10, step=5)

def fetch_order_book(symbol, limit):
    url = f"https://api.binance.com/api/v3/depth"
    params = {'symbol': symbol, 'limit': limit}
    response = requests.get(url, params=params)
    data = response.json()
    bids = [[float(p), float(q)] for p, q in data['bids']]
    asks = [[float(p), float(q)] for p, q in data['asks']]
    return bids, asks

def build_orderbook_dataframe(bids, asks):
    df_bids = pd.DataFrame(bids, columns=["price", "volume"])
    df_bids["type"] = "Bid"
    df_asks = pd.DataFrame(asks, columns=["price", "volume"])
    df_asks["type"] = "Ask"
    return pd.concat([df_bids, df_asks], ignore_index=True)

placeholder = st.empty()

# 添加循环停止控制
run = st.toggle("实时刷新", value=True)

while run:
    try:
        bids, asks = fetch_order_book(symbol, limit)
        df = build_orderbook_dataframe(bids, asks)
        fig = px.density_heatmap(
            df,
            x="type",
            y="price",
            z="volume",
            color_continuous_scale="Viridis",
            title=f"{symbol} 实时挂单热力图"
        )
        fig.update_yaxes(autorange="reversed")
        placeholder.plotly_chart(fig, use_container_width=True)
        time.sleep(refresh_interval)
    except Exception as e:
        st.error(f"出错了: {e}")
        time.sleep(refresh_interval)
