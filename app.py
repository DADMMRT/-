import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Crypto Liquidity Monitor", layout="wide")
st.title("📊 实时加密货币挂单热力图监控")

# 选择币种
symbol = st.selectbox("选择币种:", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])

# 显示深度档数
limit = st.slider("显示深度档数:", min_value=10, max_value=500, value=100, step=10)

# 刷新间隔，最少10秒
refresh_interval = st.slider("刷新间隔 (秒):", min_value=10, max_value=60, value=10, step=5)

# 自动刷新组件
st_autorefresh(interval=refresh_interval * 1000, key="refresh")

def fetch_order_book(symbol, limit):
    url = "https://api.binance.com/api/v3/depth"
    params = {'symbol': symbol, 'limit': limit}
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"API请求失败，状态码：{response.status_code}，内容：{response.text}")
    
    data = response.json()
    
    if "bids" not in data or "asks" not in data:
        raise Exception(f"API返回数据格式错误: {data}")
    
    bids = [[float(p), float(q)] for p, q in data['bids']]
    asks = [[float(p), float(q)] for p, q in data['asks']]
    return bids, asks

def build_orderbook_dataframe(bids, asks):
    df_bids = pd.DataFrame(bids, columns=["price", "volume"])
    df_bids["type"] = "Bid"
    df_asks = pd.DataFrame(asks, columns=["price", "volume"])
    df_asks["type"] = "Ask"
    return pd.concat([df_bids, df_asks], ignore_index=True)

try:
    bids, asks = fetch_order_book(symbol, limit)
except Exception as e:
    st.error(f"获取订单簿数据失败: {e}")
    st.stop()

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

st.plotly_chart(fig, use_container_width=True)

