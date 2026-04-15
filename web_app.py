import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib  # グラフの日本語化

# ------------------------------
# 1. 画面のレイアウト（UI）設定
# ------------------------------
st.set_page_config(page_title="FX CFD 分析ツール", layout="centered")
st.title("📊 FX CFD 相場分析ツール")
st.write("Pixelからも見やすい、Webアプリ版の分析ツールです。")

# 選択肢と、それに対応する期間・時間足のデータ
periods = {
    "直近1週間 (15分足)": ('5d', '15m'),
    "直近1ヶ月 (1時間足)": ('1mo', '1h'),
    "直近3ヶ月 (1時間足)": ('3mo', '1h'),
    "直近半年 (日足)": ('6mo', '1d'),
    "直近1年 (日足)": ('1y', '1d')
}

# ドロップダウンメニュー
selected_label = st.selectbox("分析したい期間を選択してください:", list(periods.keys()))
target_period, target_interval = periods[selected_label]

# ------------------------------
# 2. 実行ボタンとデータ処理
# ------------------------------
if st.button("グラフを表示する", type="primary"):
    
    # 処理中であることを示すスピナー
    with st.spinner("最新データを取得中..."):
        
        # 修正: 米ドル指数を、より取得が安定しているETF(UUP)に変更
        assets = {
            'ゴールド (金先物)': 'GC=F',
            '米国10年債先物 (価格下落＝金利上昇)': 'ZN=F',
            '米ドル連動ETF (ドル指数と同形状)': 'UUP', 
            'VIX指数 (恐怖指数)': '^VIX'
        }

        df = pd.DataFrame()
        for name, ticker in assets.items():
            try:
                ticker_data = yf.Ticker(ticker)
                hist = ticker_data.history(period=target_period, interval=target_interval)
                
                if not hist.empty:
                    if hist.index.tz is not None:
                        hist.index = hist.index.tz_localize(None)
                    df[name] = hist['Close']
            except Exception as e:
                # 取得に失敗した場合は画面上部に警告文を表示
                st.warning(f"⚠️ {name} ({ticker}) のデータ取得に一時的に失敗しました。")

        df = df.ffill().bfill()

        if df.empty:
            st.error("エラー: 有効なデータを取得できませんでした。時間をおいて再度お試しください。")
        else:
            # 取得できた銘柄の数に合わせてグラフの行数と縦幅を自動調整
            num_plots = len(df.columns)
            fig, axes = plt.subplots(nrows=num_plots, ncols=1, figsize=(8, 3 * num_plots), sharex=True)
            
            if num_plots == 1:
                axes = [axes]

            # グラフの色（ゴールド、赤、緑、紫）
            colors = ['gold', 'red', 'green', 'purple']

            for ax, column, color in zip(axes, df.columns, colors):
                ax.plot(df.index, df[column], label=column, color=color, linewidth=1.5)
                ax.set_ylabel('価格 / 指数')
                ax.grid(True, linestyle='--', alpha=0.6)
                ax.legend(loc='upper left')

            plt.xlabel('日時')
            plt.suptitle(f'市場比較チャート ({selected_label})', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.subplots_adjust(top=0.95 if num_plots > 1 else 0.90)

            # Streamlit上にグラフを描画
            st.pyplot(fig)