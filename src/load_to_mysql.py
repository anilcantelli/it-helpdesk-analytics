import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "it_helpdesk_analytics")

if not DB_PASSWORD:
    raise SystemExit(
        "DB_PASSWORD bulunamadı! Proje kök klasöründe bir '.env' dosyası oluşturup "
        "içine MySQL şifreni yazdığından emin ol (.env.example dosyasına bak)."
    )

connection_string = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

df = pd.read_csv("data/cleaned_tickets.csv")
print(f"CSV'den okunan satır sayısı: {len(df)}")

df.to_sql("tickets", con=engine, if_exists="append", index=False, chunksize=5000)

print("Yükleme tamamlandı! tickets tablosuna veri eklendi.")
