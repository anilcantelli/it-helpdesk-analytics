import pandas as pd

df = pd.read_csv("data/raw_tickets.csv")

print("=" * 60)
print("1) SATIR VE SÜTUN SAYISI")
print("=" * 60)
print(f"Satır sayısı: {df.shape[0]}")
print(f"Sütun sayısı: {df.shape[1]}")

print()
print("=" * 60)
print("2) SÜTUN TİPLERİ")
print("=" * 60)
print(df.dtypes)

print()
print("=" * 60)
print("3) EKSİK (NULL) DEĞER SAYISI - SÜTUN BAZINDA")
print("=" * 60)
print(df.isnull().sum())

print()
print("=" * 60)
print("4) İLK 3 SATIR")
print("=" * 60)
print(df.head(3).to_string())

print()
print("=" * 60)
print("5) SAYISAL SÜTUNLARIN ÖZET İSTATİSTİKLERİ")
print("=" * 60)
print(df.describe())

print()
print("=" * 60)
print("6) KATEGORİK SÜTUNLARDA BENZERSİZ DEĞERLER (priority, status, sla_plan)")
print("=" * 60)
for col in ["priority", "status", "sla_plan", "issue_type"]:
    print(f"\n-- {col} --")
    print(df[col].value_counts())
