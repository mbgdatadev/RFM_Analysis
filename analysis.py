import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


def create_rfm(dataframe, csv=False):
    # VERIYI HAZIRLAMA
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # RFM METRIKLERININ HESAPLANMASI
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                                'Invoice': lambda num: num.nunique(),
                                                "TotalPrice": lambda price: price.sum()})
    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]

    # RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    # RFM skorları kategorik değere dönüştürülüp df'e eklendi
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))

    # SEGMENTLERIN ISIMLENDIRILMESI
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm

# Veriyi yükle
df= pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2009-2010")
rfm = create_rfm(df, csv=True)

# RFM segmentlerini görselleştirme
plt.figure(figsize=(10, 6))
sns.countplot(x='segment', data=rfm, order=rfm['segment'].value_counts().index)
plt.xticks(rotation=45)
plt.title('RFM Segment Counts')
plt.xlabel('Segments')
plt.ylabel('Count')
plt.show()

# Grafik 1: RFM Segmentlerinin Dağılımı
plt.figure(figsize=(10, 6))
sns.countplot(x='segment', data=rfm, order=rfm['segment'].value_counts().index, palette='viridis')
plt.xticks(rotation=45)
plt.title('RFM Segment Counts')
plt.xlabel('Segments')
plt.ylabel('Count')
plt.savefig('rfm_segment_counts.png')
plt.show()

# Grafik 2: Recency, Frequency ve Monetary Dağılımları
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
sns.histplot(rfm['recency'], kde=True, ax=axes[0], color='blue')
axes[0].set_title('Recency Distribution')
sns.histplot(rfm['frequency'], kde=True, ax=axes[1], color='orange')
axes[1].set_title('Frequency Distribution')
sns.histplot(rfm['monetary'], kde=True, ax=axes[2], color='green')
axes[2].set_title('Monetary Distribution')
plt.savefig('rfm_distributions.png')
plt.show()

# Grafik 3: RFM Segmentlerine Göre Ortalama Recency, Frequency ve Monetary Değerleri
rfm_means = rfm.groupby('segment').agg({'recency': 'mean', 'frequency': 'mean', 'monetary': 'mean'}).reset_index()
rfm_means = pd.melt(rfm_means, id_vars=['segment'], value_vars=['recency', 'frequency', 'monetary'], var_name='Metric', value_name='Value')
plt.figure(figsize=(12, 6))
sns.barplot(x='segment', y='Value', hue='Metric', data=rfm_means, palette='viridis')
plt.xticks(rotation=45)
plt.title('Average RFM Values by Segment')
plt.xlabel('Segment')
plt.ylabel('Average Value')
plt.legend(title='Metric')
plt.savefig('rfm_segment_means.png')
plt.show()

# Grafik 4: Müşteri Segmentlerinin Ülkelere Göre Dağılımı
country_segment = df.merge(rfm, on='Customer ID').groupby(['Country', 'segment']).size().unstack().fillna(0)
plt.figure(figsize=(15, 10))
sns.heatmap(country_segment, cmap='viridis', cbar=True, linewidths=.5)
plt.title('Customer Segments by Country')
plt.xlabel('Segment')
plt.ylabel('Country')
plt.savefig('country_segments_heatmap.png')
plt.show()