###############################################################
# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)
###############################################################
###############################################################
# İş Problemi (Business Problem)
###############################################################
#Online ayakkabı mağazası olan FLO müşterilerini segmentlere ayırıp bu segmentlere göre pazarlama stratejileri belirlemek istiyor.
#Buna yönelik olarak müşterilerin davranışları tanımlanacak ve bu davranışlardaki öbeklenmelere göre gruplar oluşturulacak.

###############################################################
# Veri Seti Hikayesi
###############################################################
# Veri seti son alışverişlerini 2020 - 2021 yıllarında OmniChannel(hem online hem offline alışveriş yapan) olarak yapan müşterilerin geçmiş alışveriş davranışlarından
# elde edilen bilgilerden oluşmaktadır.
# master_id: Eşsiz müşteri numarası
# order_channel : Alışveriş yapılan platforma ait hangi kanalın kullanıldığı (Android, ios, Desktop, Mobile, Offline)
# last_order_channel : En son alışverişin yapıldığı kanal
# first_order_date : Müşterinin yaptığı ilk alışveriş tarihi
# last_order_date : Müşterinin yaptığı son alışveriş tarihi
# last_order_date_online : Muşterinin online platformda yaptığı son alışveriş tarihi
# last_order_date_offline : Muşterinin offline platformda yaptığı son alışveriş tarihi
# order_num_total_ever_online : Müşterinin online platformda yaptığı toplam alışveriş sayısı
# order_num_total_ever_offline : Müşterinin offline'da yaptığı toplam alışveriş sayısı
# customer_value_total_ever_offline : Müşterinin offline alışverişlerinde ödediği toplam ücret
# customer_value_total_ever_online : Müşterinin online alışverişlerinde ödediği toplam ücret
# interested_in_categories_12 : Müşterinin son 12 ayda alışveriş yaptığı kategorilerin listesi

############################################################
# Görev-1: Veriyi Anlama (Data Understanding) ve Hazırlama
############################################################
# Adım 1: flo_data_20K.csv verisini okuyunuz.Dataframe’in kopyasını oluşturunuz.

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)
df_ = pd.read_csv("C:/Users/ASUS/PycharmProjects/ödev/3. Hafta/FLO_RFM_Analizi/flo_data_20k.csv")
df = df_.copy()

# Adım 2:
# a)İlk 10 gözlem
df.head(10)
# b)Değişken isimler
df.columns
# c)Betimsel istatistik
df.describe().T
# d)Boş değer
df.isnull().sum()
# e)Değişken tipleri, incelemesi yapınız
df.info()

# Adım 3: Omnichannel müşterilerin hem online'dan hemde offline platformlardan alışveriş yaptığını ifade etmektedir.
# Her bir müşterinin toplam alışveriş sayısı ve harcaması için yeni değişkenler oluşturunuz.

df["omnichannel_order_num_totel"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["omnichannel_customer_value_totel"] = df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]

# Adım 4: Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz.

df.columns
for i in df.columns:
    if "date" in i:
        df[i]=df[i].astype("datetime64[ns]")

# Adım 5: Alışveriş kanallarındaki müşteri sayısının, toplam alınan ürün sayısının ve toplam harcamaların dağılımına bakınız.

df["omnichannel_order_num_totel"].head()
df["omnichannel_customer_value_totel"].head()


# Adım 6: En fazla kazancı getiren ilk 10 müşteriyi sıralayınız.

df.groupby("master_id").agg({ "omnichannel_customer_value_totel":"sum"}).sort_values(by="omnichannel_customer_value_totel", ascending=False).head(10)

#Adım 7: En fazla siparişi veren ilk 10 müşteriyi sıralayınız.

df.groupby("master_id").agg({"omnichannel_order_num_totel":"sum"}).sort_values(by="omnichannel_order_num_totel", ascending=False).head(10)

#Adım 8: Veri ön hazırlık sürecini fonksiyonlaştırınız.
df.head()
df["last_order_date"].max()
today_date = dt.datetime(2021,6,1)
type(today_date)

#Görev 2: RFM Metriklerinin Hesaplanması
rfm = df.groupby("master_id").agg({"last_order_date": lambda last_order_date: (today_date - last_order_date.max()).days,
                                     "omnichannel_order_num_totel": lambda omnichannel_order_num_totel : omnichannel_order_num_totel.nunique(),
                                     "omnichannel_customer_value_totel": lambda omnichannel_customer_value_totel: omnichannel_customer_value_totel.sum()})

rfm.head()

rfm.columns = ['recency', 'frequency', 'monetary']

rfm.describe().T

rfm = rfm[rfm["monetary"] > 0]
rfm.shape

#Görev 3: RF Skorunun Hesaplanması
#Adım 1: Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.
#Adım 2: Bu skorları recency_score, frequency_score ve monetary_score olarak kaydediniz.


rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])

# 0-100, 0-20, 20-40, 40-60, 60-80, 80-100

rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

#Adım 3: recency_score ve frequency_score’u tek bir değişken olarak ifade ediniz ve RF_SCORE olarak kaydediniz.

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))
rfm.describe().T

#Görev 4: RF Skorunun Segment Olarak Tanımlanması
#Adım 1: Oluşturulan RF skorları için segment tanımlamaları yapınız.
#Adım 2: Aşağıdaki seg_map yardımı ile skorları segmentlere çeviriniz.

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
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

#Görev 5: Aksiyon Zamanı
#Adım 1: Segmentlerin recency, frequnecy ve monetary ortalamalarını inceleyiniz.

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean"])

#Adım 2: RFM analizi yardımıyla aşağıda verilen 2 case için ilgili profildeki müşterileri bulun ve müşteri id'lerini csv olarak kaydediniz.
#a. FLO bünyesine yeni bir kadın ayakkabı markası dahil ediyor. Dahil ettiği markanın ürün fiyatları genel müşteri
# tercihlerinin üstünde. Bu nedenle markanın tanıtımı ve ürün satışları için ilgilenecek profildeki müşterilerle özel olarak
#iletişime geçmek isteniliyor. Sadık müşterilerinden(champions, loyal_customers) ve kadın kategorisinden alışveriş
#yapan kişiler özel olarak iletişim kurulacak müşteriler. Bu müşterilerin id numaralarını csv dosyasına kaydediniz.

women=df[(df["interested_in_categories_12"]).str.contains("KADIN")]
high_value_customers= rfm[(rfm["segment"].isin(["champions","loyal_customers"]))]
w_hvc=pd.merge(women,high_value_customers, on=["master_id"])

#b. Erkek ve Çocuk ürünlerinde %40'a yakın indirim planlanmaktadır.
# u indirimle ilgili kategorilerle ilgilenen geçmişte iyi müşteri olan ama uzun süredir alışveriş yapmayan kaybedilmemesi gereken müşteriler,
# uykuda olanlar ve yeni gelen müşteriler özel olarak hedef alınmak isteniyor. Uygun profildeki müşterilerin id'lerini csv dosyasına kaydediniz.

men_child=df[(df["interested_in_categories_12"]).str.contains("ERKEK", "COCUK")]
attention_customers= rfm[(rfm["segment"].isin(["cant_loose","about_to_sleep","new_customers"]))]
mc_ac=pd.merge(men_child,attention_customers, on=["master_id"])

w_hvc.to_csv("w_hvc.csv")
mc_ac.to_csv("mc_ac.csv")








