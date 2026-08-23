import os
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "it_helpdesk_analytics")

if not DB_PASSWORD:
    raise SystemExit("DB_PASSWORD bulunamadı! .env dosyanı kontrol et.")

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"

CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
               "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

ISSUE_TYPE_COLORS = dict(zip(
    sorted(["account_access", "billing_problem", "bug", "feature_request",
            "how_to", "other", "performance", "security_concern"]),
    CATEGORICAL,
))
CHANNEL_COLORS = dict(zip(
    sorted(["chat", "email", "in_app", "phone_transcript", "web_form"]),
    CATEGORICAL[:5],
))

PRIORITY_ORDER = ["low", "medium", "high", "urgent"]
PRIORITY_RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab"]

SLA_PLAN_ORDER = ["standard", "gold", "platinum"]
SLA_PLAN_RAMP = ["#86b6ef", "#3987e5", "#184f95"]

TR_ISSUE_TYPE = {
    "account_access": "Hesap Erişimi",
    "billing_problem": "Faturalama Sorunu",
    "bug": "Hata (Bug)",
    "feature_request": "Özellik Talebi",
    "how_to": "Nasıl Yapılır",
    "other": "Diğer",
    "performance": "Performans",
    "security_concern": "Güvenlik Endişesi",
}
TR_PRIORITY = {"low": "Düşük", "medium": "Orta", "high": "Yüksek", "urgent": "Acil"}
TR_SLA_PLAN = {"standard": "Standart", "gold": "Altın", "platinum": "Platin"}
TR_CHANNEL = {
    "chat": "Sohbet",
    "email": "E-posta",
    "in_app": "Uygulama İçi",
    "phone_transcript": "Telefon",
    "web_form": "Web Formu",
}


def style_axes(ax):
    ax.set_facecolor(SURFACE)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(INK_MUTED)
    ax.tick_params(colors=INK_MUTED)
    ax.grid(axis="x", color=GRIDLINE, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def save_hbar(df, label_col, value_col, colors, title, xlabel, filename, value_fmt="{:.0f}"):
    fig, ax = plt.subplots(figsize=(8, 5), facecolor=SURFACE)
    df = df.sort_values(value_col)
    bars = ax.barh(df[label_col], df[value_col], color=colors, height=0.6, zorder=3)
    for bar, val in zip(bars, df[value_col]):
        ax.text(bar.get_width() + df[value_col].max() * 0.01, bar.get_y() + bar.get_height() / 2,
                value_fmt.format(val), va="center", ha="left", color=INK_PRIMARY, fontsize=9)
    style_axes(ax)
    ax.set_title(title, color=INK_PRIMARY, fontsize=13, loc="left", pad=12)
    ax.set_xlabel(xlabel, color=INK_MUTED, fontsize=9)
    fig.tight_layout()
    fig.savefig(f"dashboard/{filename}", dpi=150, facecolor=SURFACE)
    plt.close(fig)
    print(f"  kaydedildi: dashboard/{filename}")


print("MySQL'den veri çekiliyor ve grafikler oluşturuluyor...")

df1 = pd.read_sql("""
    SELECT issue_type, COUNT(*) AS ticket_count
    FROM tickets GROUP BY issue_type
""", engine)
df1 = df1.sort_values("ticket_count")
colors1 = [ISSUE_TYPE_COLORS[t] for t in df1["issue_type"]]
df1["issue_type_tr"] = df1["issue_type"].map(TR_ISSUE_TYPE)
save_hbar(df1, "issue_type_tr", "ticket_count", colors1,
          "Konu türüne göre talep sayısı", "Talep sayısı",
          "01_issue_type_distribution.png")

df2 = pd.read_sql("""
    SELECT priority, AVG(resolution_time_hours) AS avg_hours
    FROM tickets WHERE is_closed = TRUE GROUP BY priority
""", engine)
df2["priority"] = pd.Categorical(df2["priority"], categories=PRIORITY_ORDER, ordered=True)
df2 = df2.sort_values("priority")
df2["priority_tr"] = df2["priority"].map(TR_PRIORITY)
save_hbar(df2, "priority_tr", "avg_hours",
          PRIORITY_RAMP,
          "Önceliğe göre ortalama çözüm süresi (saat)", "Saat",
          "02_resolution_by_priority.png", value_fmt="{:.1f}")

df3 = pd.read_sql("""
    SELECT sla_plan,
           ROUND(SUM(CASE
               WHEN sla_plan = 'standard' AND resolution_time_hours > 48 THEN 1
               WHEN sla_plan = 'gold' AND resolution_time_hours > 24 THEN 1
               WHEN sla_plan = 'platinum' AND resolution_time_hours > 8 THEN 1
               ELSE 0 END) / COUNT(*) * 100, 1) AS breach_rate_pct
    FROM tickets WHERE is_closed = TRUE GROUP BY sla_plan
""", engine)
df3["sla_plan"] = pd.Categorical(df3["sla_plan"], categories=SLA_PLAN_ORDER, ordered=True)
df3 = df3.sort_values("sla_plan")
df3["sla_plan_tr"] = df3["sla_plan"].map(TR_SLA_PLAN)
save_hbar(df3, "sla_plan_tr", "breach_rate_pct",
          SLA_PLAN_RAMP,
          "SLA planına göre aşım oranı (%) - varsayılan hedefler: Standart 48s / Altın 24s / Platin 8s",
          "Aşım oranı (%)", "03_sla_breach_by_plan.png", value_fmt="{:.1f}%")

df4 = pd.read_sql("""
    SELECT issue_type, AVG(csat_score) AS avg_csat
    FROM tickets WHERE is_rated = TRUE GROUP BY issue_type
""", engine)
df4 = df4.sort_values("avg_csat")
colors4 = [ISSUE_TYPE_COLORS[t] for t in df4["issue_type"]]
df4["issue_type_tr"] = df4["issue_type"].map(TR_ISSUE_TYPE)
save_hbar(df4, "issue_type_tr", "avg_csat", colors4,
          "Konu türüne göre ortalama memnuniyet (CSAT, 0-5)", "Ortalama CSAT",
          "04_csat_by_issue_type.png", value_fmt="{:.2f}")

df5 = pd.read_sql("""
    SELECT channel, ROUND(SUM(reopened) / COUNT(*) * 100, 1) AS reopen_rate_pct
    FROM tickets GROUP BY channel
""", engine)
df5 = df5.sort_values("reopen_rate_pct")
colors5 = [CHANNEL_COLORS[c] for c in df5["channel"]]
df5["channel_tr"] = df5["channel"].map(TR_CHANNEL)
save_hbar(df5, "channel_tr", "reopen_rate_pct", colors5,
          "Kanala göre yeniden açılma oranı (%)", "Yeniden açılma oranı (%)",
          "05_reopen_rate_by_channel.png", value_fmt="{:.1f}%")

print("\nTüm grafikler dashboard/ klasörüne kaydedildi.")
