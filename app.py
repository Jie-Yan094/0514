import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

# 從 Streamlit Secrets 讀取 GEE 服務帳戶金鑰 JSON
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]
# 使用 google-auth 進行 GEE 授權
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)
# 初始化 GEE
ee.Initialize(credentials)
###############################################
st.set_page_config(layout="wide")
st.title("🌍 使用服務帳戶連接 GEE 的 Streamlit App")
###############################################
# 地理區域
point = ee.Geometry.Point([120.5583462887228, 24.081653403304525])

# 擷取 Sentinel-2
image = ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
    .filterBounds(point) \
    .filterDate('2021-01-01', '2022-01-01') \
    .sort('CLOUDY_PIXEL_PERCENTAGE') \
    .first() \
    .select('B.*')
vis_params = {'min': 100,'max': 3500,'bands': ['B11', 'B8', 'B3']}

if image is not None:
    st.success("成功找到 Sentinel-2 影像！")
    # ... 後續程式碼 ...
else:
    st.error("沒有找到符合篩選條件的 Sentinel-2 影像。")

# 建立訓練資料
training001 = image.sample(
    **{
        'region': image.geometry(),
        'scale': 10,
        'numPixels': 10000,
        'seed': 0,
        'geometries': True,
    }
)
# 使用 wekaKMeans分群器
n_clusters = 11
clusterer_KMeans = ee.Clusterer.wekaKMeans(nClusters=n_clusters).train(training001)
result001 = image.cluster(clusterer_KMeans)
legend_dict = {
    '0': '#1c5f2c',
    '1': '#ab0000',
    '2': '#d99282',
    '3': '#ff0004',
    '4': '#ab6c28',
    '5': '#466b9f',
    '6': '#10d22c',
    '7': '#fae6a0',
    '8': '#f0f0f0',
    '9': '#58481f',
    '10':'#ab0000'
}
palette = list(legend_dict.values())
vis_params_001 = {'min': 0, 'max': 10, 'palette': palette}


# 顯示地圖
Map = geemap.Map(center=[120.5583462887228, 24.081653403304525], zoom=9)
Map.addLayer(image, vis_params, "Sentinel-2")
Map.to_streamlit(height=600)
