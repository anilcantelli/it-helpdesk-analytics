import os
import random
from datetime import datetime, timedelta

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "it_helpdesk_analytics")

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS demo_errors"))
    conn.execute(text("""
        CREATE TABLE demo_errors (
            error_id INT PRIMARY KEY AUTO_INCREMENT,
            error_date DATE NOT NULL,
            error_type VARCHAR(30) NOT NULL
        )
    """))
    conn.commit()
print("1) demo_errors tablosu oluşturuldu.")

ERROR_TYPES = ["timeout", "null_pointer", "connection_lost", "permission_denied"]
today = datetime(2026, 8, 23)
three_months_ago = today - timedelta(days=90)

random.seed(42)
rows = []
for _ in range(200):
    random_day_offset = random.randint(0, 90)
    error_date = three_months_ago + timedelta(days=random_day_offset)
    error_type = random.choice(ERROR_TYPES)
    rows.append({"error_date": error_date.date(), "error_type": error_type})

df = pd.DataFrame(rows)
print(f"2) {len(df)} rastgele hata kaydı üretildi (bellekte, henüz veritabanında değil).")

df.to_sql("demo_errors", con=engine, if_exists="append", index=False)
print("3) Kayıtlar demo_errors tablosuna eklendi.")

result = pd.read_sql("""
    SELECT error_type, COUNT(*) AS adet
    FROM demo_errors
    GROUP BY error_type
    ORDER BY adet DESC
""", engine)
print("4) SQL sorgusunun cevabı:")
print(result.to_string(index=False))

fig, ax = plt.subplots(figsize=(7, 4), facecolor="#fcfcfb")
ax.bar(result["error_type"], result["adet"], color="#2a78d6")
ax.set_title("3 aylık test - hata türüne göre adet (rastgele üretilen örnek veri)")
ax.set_ylabel("Adet")
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
fig.tight_layout()
fig.savefig("dashboard/demo_errors.png", dpi=150, facecolor="#fcfcfb")
plt.close(fig)
print("5) Grafik kaydedildi: dashboard/demo_errors.png")
