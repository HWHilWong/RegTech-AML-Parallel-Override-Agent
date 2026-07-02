import streamlit as st
import pandas as pd
import numpy as np
import ollama
import os

# --- 網頁前端配置 ---
st.set_page_config(page_title="國際銀行 AML AI Investigator Agent", layout="wide")
st.title("🕵️‍♂️ 國際銀行 AML AI Investigator Agent (RegTech 2.0)")
st.subheader("由傳統規則與 XGBoost 並聯交叉驗證，並結合本地 Llama 3 驅動的自動化審查系統")

# --- 側邊欄：合規與安全配置 ---
st.sidebar.header("🔒 銀行合規與數據安全配置")
st.sidebar.success("數據駐留狀態：本地 On-premise (符合 HKMA 指引)")
st.sidebar.info("LLM 引擎：Ollama - Llama 3 (100% 離線內網運行)")

# 讓合規官彈性調整 AI 門檻
risk_threshold = st.sidebar.slider("設定 AI 異常分數報警門檻 (Risk Threshold)", 0.50, 0.95, 0.80, step=0.05)

# 讓合規官彈性調整傳統 Rule-based 的大額轉帳閾值
rule_amount_limit = st.sidebar.number_input("設定傳統規則：大額轉帳警告門檻 (HKD)", value=50000, step=5000)

# --- 主畫面：上傳大數據檔案 ---
uploaded_file = st.file_uploader("📂 請上傳銀行原始交易流水檔案 (CSV 格式)", type=["csv"])

if uploaded_file is not None:
    st.info("🚀 數據已讀入，正在啟動【傳統規則 A】與【AI 模型 B】並聯交叉驗證引擎...")
    
    # 讀取數據 (為了前端流暢度，預設讀取前 20,000 筆)
    raw_df = pd.read_csv(uploaded_file, nrows=20000)
    df = raw_df.copy()
    
    # ─── 管道 A：傳統 Rule-based 檢查 (事後監察：TRANSFER 且大於設定閾值)
    df['hit_traditional_rule'] = ((df['type'] == 'TRANSFER') & (df['amount'] >= rule_amount_limit)).astype(int)
    
    # ─── 管道 B：AI 核心行為特徵工程
    df['is_C2C'] = ((df['nameOrig'].str.startswith('C')) & (df['nameDest'].str.startswith('C'))).astype(int)
    df['is_round_amount'] = (df['amount'] % 1 == 0).astype(int)
    df['is_near_threshold'] = ((df['amount'] >= 90000) & (df['amount'] <= 100000)).astype(int)
    for t in ['CASH_IN', 'CASH_OUT', 'DEBIT', 'PAYMENT', 'TRANSFER']:
        df[f'type_{t}'] = (df['type'] == t)
        
    # 模擬 XGBoost 模型打分 (此處沿用你埋入的 42712 交易觸發 0.8118 分數，其餘隨機)
    np.random.seed(42)
    scores = np.random.uniform(0.05, 0.45, size=len(df))
    # 讓第一筆交易（amount=42712.39）精確拿到 0.8118
    scores[0] = 0.8118 
    df['ml_risk_score'] = scores
    
    # ─── 管道 C：決策矩陣交叉比對 (Parallel Override Logic)
    final_tags = []
    agent_actions = []
    
    for idx, row in df.iterrows():
        is_rule_hit = row['hit_traditional_rule'] == 1
        ai_score = row['ml_risk_score']
        
        if is_rule_hit and ai_score >= risk_threshold:
            final_tags.append("🔴 Critical (雙重命中)")
            agent_actions.append("TRIGGER_AGENT_SAR")
        elif is_rule_hit and ai_score < risk_threshold:
            final_tags.append("🟡 Medium (AI低分，但傳統規則強制覆蓋)")
            agent_actions.append("ROUTE_TO_MANUAL_INVESTIGATION")
        elif not is_rule_hit and ai_score >= risk_threshold:
            final_tags.append("🟠 High (規則漏報，但 AI 成功預警)")
            agent_actions.append("TRIGGER_AGENT_SAR")
        else:
            final_tags.append("🟢 Low (雙重無異常)")
            agent_actions.append("AUTO_ARCHIVE")
            
    df['final_risk_tag'] = final_tags
    df['agent_action'] = agent_actions
    
    # --- 前端展示統計結果 ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔴 Critical/High (需要 Agent 寫報告)", len(df[df['agent_action'] == "TRIGGER_AGENT_SAR"]))
    with col2:
        st.metric("🟡 Medium (需要人工調查兜底)", len(df[df['agent_action'] == "ROUTE_TO_MANUAL_INVESTIGATION"]))
    with col3:
        st.metric("🟢 Low (安全直接歸檔)", len(df[df['agent_action'] == "AUTO_ARCHIVE"]))
        
    st.write("### 📋 交叉驗證審計流水線 (Auditing Pipeline Preview)")
    # 挑選核心欄位展示
    show_cols = ['step', 'type', 'amount', 'hit_traditional_rule', 'ml_risk_score', 'final_risk_tag', 'agent_action']
    st.dataframe(df[show_cols].head(10))
    
    # --- Agent 自動化 SAR 報告生成 ---
    trigger_cases = df[df['agent_action'] == "TRIGGER_AGENT_SAR"]
    
    if len(trigger_cases) > 0:
        st.write("### 🧠 AI Agent 深度審計個案")
        target_case = trigger_cases.iloc[0]
        
        st.warning(f"偵測到高風險交易！類型: {target_case['final_risk_tag']} | 金額: HKD {target_case['amount']} | AI 分數: {target_case['ml_risk_score']:.4f}")
        
        if st.button("✨ 一鍵啟動 AI Agent 生成可解釋性 SAR 報告"):
            with st.spinner("🧠 正在調用本地 Llama 3 進行合規推理與法律草稿撰寫..."):
                try:
                    evidence = {
                        'step': target_case['step'], 'type': target_case['type'], 'amount': target_case['amount'],
                        'hit_traditional_rule': target_case['hit_traditional_rule'], 'ml_risk_score': f"{target_case['ml_risk_score']:.4f}",
                        'is_C2C': target_case['is_C2C'], 'is_near_threshold': target_case['is_near_threshold']
                    }
                    system_prompt = f"""
                    You are a Senior MLRO at an international bank in Hong Kong. 
                    Write a highly professional SAR Narrative (JFIU standard) based on this parallel validation evidence.
                    Explain why the alert category '{target_case['final_risk_tag']}' warrants investigation.
                    Focus on behavioral risk. Keep the tone analytical and cold.
                    """
                    response = ollama.chat(model='llama3', messages=[
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': str(evidence)},
                    ])
                    
                    report_content = response['message']['content']
                    st.success("✅ SAR 報告草稿生成成功！")
                    st.text_area("📄 JFIU 標準 SAR 報告草稿", report_content, height=350)
                    
                    st.download_button(
                        label="💾 下載此報告草稿",
                        data=report_content,
                        file_name=f"SAR_REPORT_{target_case['final_risk_tag']}.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"連線失敗，請確保 Ollama 正在後台運行。錯誤: {e}")