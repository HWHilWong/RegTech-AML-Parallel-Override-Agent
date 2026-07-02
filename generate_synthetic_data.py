import pandas as pd
import numpy as np
import random
import time

def generate_aml_dataset():
    print("⏳ [RegTech 2.0 Engine] 正在為你生成 250MB 的高保真 AML 模擬數據集...")
    start_time = time.time()

    # 1. 定義生成規模：200 萬筆數據大約會產生 230MB - 250MB 的 CSV 檔案
    num_rows = 2000000

    # 2. 模擬基礎流水欄位
    print("🧬 正在構建基礎交易欄位（NumPy 加速中）...")
    steps = np.random.randint(1, 50, size=num_rows)
    types = np.random.choice(
        ['CASH_IN', 'CASH_OUT', 'DEBIT', 'PAYMENT', 'TRANSFER'], 
        size=num_rows, 
        p=[0.2, 0.35, 0.05, 0.3, 0.1]
    )
    amounts = np.round(np.random.exponential(scale=5000, size=num_rows) + 10, 2)

    # 3. 模擬帳戶 ID (C 代表一般客戶，M 代表商戶)
    print("🆔 正在模擬銀行帳戶 ID 流水 (M/C 帳戶分流)...")
    orig_ids = [f"C{random.randint(1000000, 9999999)}" for _ in range(num_rows)]
    dest_ids = []
    for t in types:
        if t == 'PAYMENT':
            dest_ids.append(f"M{random.randint(1000000, 9999999)}")
        else:
            dest_ids.append(f"C{random.randint(1000000, 9999999)}")

    # 4. 模擬餘額流水 (即使特徵工程優化後拔除了它，PaySim 標準格式仍必須包含)
    old_balance_org = np.round(np.random.exponential(scale=20000, size=num_rows), 2)
    new_balance_orig = np.maximum(0, old_balance_org - amounts)
    old_balance_dest = np.round(np.random.exponential(scale=50000, size=num_rows), 2)
    new_balance_dest = old_balance_dest + amounts

    # 5. 初始化監管標籤
    is_fraud = np.zeros(num_rows, dtype=int)
    is_flagged_fraud = np.zeros(num_rows, dtype=int)

    # 📋 核心安全網測試：故意在最前面塞入「高風險洗錢個案」以供 Agent 進行端到端測試
    # 模式：大額 C2C TRANSFER 交易，且金額吻合你之前抓到的特徵（用於觸發 0.8118 分數）
    print("🚨 正在注入結構化洗錢測試樣本（數據注入測試）...")
    for i in range(5):
        steps[i] = 1
        types[i] = 'TRANSFER'
        amounts[i] = 42712.39  
        orig_ids[i] = "C9999999"
        dest_ids[i] = "C8888888"
        is_fraud[i] = 1

    # 6. 組裝成與原始 PaySim 100% 相同的 11 個標準欄位 DataFrame
    print("📦 正在封裝 11 欄位標準金融矩陣...")
    synthetic_df = pd.DataFrame({
        'step': steps,
        'type': types,
        'amount': amounts,
        'nameOrig': orig_ids,
        'oldbalanceOrg': old_balance_org,
        'newbalanceOrig': new_balance_orig,
        'nameDest': dest_ids,
        'oldbalanceDest': old_balance_dest,
        'newbalanceDest': new_balance_dest,
        'isFraud': is_fraud,
        'isFlaggedFraud': is_flagged_fraud
    })

    # 7. 導出成大檔案
    output_filename = 'synthetic_banking_log.csv'
    print(f"💾 正在寫入硬碟磁區：{output_filename} ...")
    synthetic_df.to_csv(output_filename, index=False)

    end_time = time.time()
    elapsed = end_time - start_time
    
    print("\n" + "="*50)
    print(f"✅ 高保真數據集建立成功！耗時: {elapsed:.2f} 秒")
    print(f"📊 數據規模：{len(synthetic_df):,} 筆交易流水")
    print(f"⚠️ 安全提示：已成功注入測試用嫌疑洗錢特徵樣本")
    print(f"📌 請立刻在 PowerShell 執行 'streamlit run app.py --server.maxUploadSize 2048' 進行展示！")
    print("="*50)

if __name__ == "__main__":
    generate_aml_dataset()