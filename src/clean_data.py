import pandas as pd

df = pd.read_csv("data/raw_tickets.csv")

df["created_at"] = pd.to_datetime(df["created_at"])

df["region"] = df["region"].fillna("unknown")

df["is_closed"] = df["status"].isin(["resolved", "closed_no_action"])

df["is_rated"] = df["csat_score"] > 0

assert df["ticket_id"].is_unique, "Dikkat: tekrar eden ticket_id bulundu!"

df.to_csv("data/cleaned_tickets.csv", index=False)

print("Temizlenmiş veri kaydedildi: data/cleaned_tickets.csv")
print(f"Toplam satır: {len(df)}")
print(f"Kapanmış (is_closed=True) ticket sayısı: {df['is_closed'].sum()}")
print(f"Puanlanmış (is_rated=True) ticket sayısı: {df['is_rated'].sum()}")
print(f"region='unknown' olarak doldurulan satır sayısı: {(df['region'] == 'unknown').sum()}")
