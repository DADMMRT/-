import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="OKEx Liquidity Monitor", layout="wide")
st.title("📊 实时 OKEx 加密货币挂单热力图")

# 币种选择，OKEx 使用连接符 "-" 表示交易对
symbol = st.selectbox("选择币种:", ["BTC-USDT", "ETH-USDT", "SOL-USDT"])

# 深度档位
limit = st.slider("显示深度档数:", min_value=10, max_value=400, value=100, step=10)

# 刷新间隔
refresh_interval = st.slider("刷新间隔 (秒):", min_value=10, max_value=60, value=10, step=5)

# 自动刷新
st_autorefresh(interval=refresh_interval * 1000, key="refresh")

# 获取 OKEx 订单簿数据
def fetch_order_book_okx(symbol, limit):
    url = "https://www.okx.com/api/v5/market/books"
    params = {"instId": symbol, "sz": limit}
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"OKEx API 请求失败，状态码: {response.status_code}，内容: {response.text}")
    
    data = response.json()
    
    if "data" not in data or len(data["data"]) == 0:
        raise Exception(f"OKEx 返回数据为空或格式错误: {data}")
    
    book = data["data"][0]
   bids = [[float(p[0]), float(p[1])] for p in book['bids']]
asks = [[float(p[0]), float(p[1])] for p in book['asks']]
    return bids, asks

# 转为DataFrame
def build_orderbook_dataframe(bids, asks):
    df_bids = pd.DataFrame(bids, columns=["price", "volume"])
    df_bids["type"] = "Bid"
    df_asks = pd.DataFrame(asks, columns=["price", "volume"])
    df_asks["type"] = "Ask"
    return pd.concat([df_bids, df_asks], ignore_index=True)

# 获取和可视化
try:
    bids, asks = fetch_order_book_okx(symbol, limit)
    df = build_orderbook_dataframe(bids, asks)
    
    fig = px.density_heatmap(
        df,
        x="type",
        y="price",
        z="volume",
        color_continuous_scale="Viridis",
        title=f"{symbol} 实时挂单热力图（来自 OKEx）"
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"获取订单簿数据失败: {e}")
