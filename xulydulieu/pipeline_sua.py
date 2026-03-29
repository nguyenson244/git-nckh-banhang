import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler

def run_pipeline():
    current_dir = os.path.dirname(os.path.abspath(__file__)) # Thư mục xulydulieu
    parent_dir = os.path.dirname(current_dir) # Thư mục gốc git-nckh-banhang-main
    data_folder = os.path.join(parent_dir, 'data')
    target_folder = current_dir
    
    # 1. READ AND COMBINE
    file_names = ['data_2023.csv', 'data_2024.csv', 'data_2025.csv']
    dfs = []
    print("--- BẮT ĐẦU ĐỌC DỮ LIỆU ---")
    for file_name in file_names:
        file_path = os.path.join(data_folder, file_name)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            dfs.append(df)
            print(f"Đã đọc file: {file_name}")
        else:
            print(f"Cảnh báo: Không tìm thấy file {file_path}")
            
    if not dfs:
        print("Không có dữ liệu nào được đọc.")
        return
        
    df_tong = pd.concat(dfs, ignore_index=True)
    all_output_file = os.path.join(target_folder, 'data_all_sua.csv')
    df_tong.to_csv(all_output_file, index=False)
    print(f"Đã xuất toàn bộ dữ liệu ra file: {all_output_file}\n")
    
    # 2. XULY DULIEU (Data Processing)
    print("--- BẮT ĐẦU XỬ LÝ DỮ LIỆU ---")
    df = df_tong.copy()
    initial_shape = df.shape
    df = df.drop_duplicates()
    print(f"- Đã xóa {initial_shape[0] - df.shape[0]} dòng trùng lặp.")
    
    # NOTE: The instruction was clearly to remove the filter for "Kinh Đô"
    # we DO NOT filter the dataset -> process everything
    
    # Xử lý missing
    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna(df[col].median())
            
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        if df[col].isnull().sum() > 0:
            modes = df[col].mode()
            if not modes.empty:
                df[col] = df[col].fillna(modes[0])
    print("- Đã xử lý dữ liệu bị thiếu (missing values).")
    
    if 'ACTUALSHIPDATE' in df.columns:
        df['ACTUALSHIPDATE'] = pd.to_datetime(df['ACTUALSHIPDATE'], errors='coerce')
        df = df.dropna(subset=['ACTUALSHIPDATE'])
        print("- Đã chuyển đổi kiểu ngày tháng (Datetime).")
        
    for col in ['Total QTY', 'Total CBM']:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers_condition = (df[col] < lower_bound) | (df[col] > upper_bound)
            outliers_count = outliers_condition.sum()
            df = df[~outliers_condition]
            print(f"- Đã xử lý {outliers_count} outliers cho cột {col}.")
            
    le = LabelEncoder()
    cols_to_encode = ['CATEGORY', 'WHSEID', 'BRAND', 'Week']
    for col in cols_to_encode:
        if col in df.columns:
            df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
    print("- Đã hoàn thành mã hóa (Encoding) biến phân loại.")
            
    scaler = StandardScaler()
    cols_to_scale = ['Total QTY', 'Total CBM']
    existing_cols = [col for col in cols_to_scale if col in df.columns]
    if existing_cols:
        df[existing_cols] = scaler.fit_transform(df[existing_cols])
        print("- Đã hoàn thành chuẩn hóa cấu hình giá trị (Scaling).")
        
    if 'ACTUALSHIPDATE' in df.columns:
        df = df.sort_values(by='ACTUALSHIPDATE', ascending=True)
        print("- Đã sắp xếp dữ liệu theo chiều thời gian.")
        
    processed_output = os.path.join(target_folder, 'data_processed_sua.csv')
    df.to_csv(processed_output, index=False)
    print(f"=> Hoàn tất xử lý. Dữ liệu đã được lưu vào: {processed_output}\n")
    
    # 3. FEATURE ENGINEERING
    print("--- BẮT ĐẦU FEATURE ENGINEERING (TRÍCH XUẤT ĐẶC TRƯNG) ---")
    if 'ACTUALSHIPDATE' in df.columns:
        df = df.sort_values(by=['BRAND', 'ACTUALSHIPDATE']).reset_index(drop=True)

    print("1. Đang tạo đặc trưng về Thời gian (Tháng, Quý, Cao điểm)...")
    if 'ACTUALSHIPDATE' in df.columns:
        df['Month'] = df['ACTUALSHIPDATE'].dt.month
        df['Quarter'] = df['ACTUALSHIPDATE'].dt.quarter
        df['DayOfWeek'] = df['ACTUALSHIPDATE'].dt.dayofweek
        df['Is_Weekend'] = df['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)
        df['Is_High_Season'] = df['Month'].apply(lambda x: 1 if x in [6, 7, 8] else 0)
        df['Is_Low_Season'] = df['Month'].apply(lambda x: 1 if x in [1, 2, 3, 4] else 0)

    print("2. Đang tạo đặc trưng Tình trạng Thương hiệu...")
    if 'BRAND' in df.columns:
        df['Is_Bread_Product'] = df['BRAND'].apply(lambda x: 1 if 'BREAD' in str(x).upper() else 0)
        df['Risk_Outlier_Brand'] = df['BRAND'].apply(lambda x: 1 if any(word in str(x).upper() for word in ['CAKE', 'BISCUIT']) else 0)

    print("3. Đang tạo đặc trưng Tương tác Thể tích - Sản lượng...")
    if 'Total QTY' in df.columns and 'Total CBM' in df.columns:
        df['QTY_CBM_Interact'] = df['Total QTY'] * df['Total CBM']
        df['Space_Loss_Factor'] = df['Total QTY'] - df['Total CBM']

    print("4. Đang tạo đặc trưng Trượt quá khứ (Rolling Lags) để dò xu hướng...")
    if 'BRAND' in df.columns and 'Total QTY' in df.columns and 'ACTUALSHIPDATE' in df.columns:
        df['QTY_Rolling_7_Days'] = df.groupby('BRAND')['Total QTY'].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
        df['QTY_Std_7_Days']   = df.groupby('BRAND')['Total QTY'].transform(lambda x: x.rolling(window=7, min_periods=1).std())

    # Thay thế các NaN do phép chia, std sinh ra bằng 0
    df = df.fillna(0)
    
    featured_output = os.path.join(target_folder, 'data_featured_sua.csv')
    df.to_csv(featured_output, index=False)
    
    print(f"\n=> Đặc trưng mới đã được kỹ sư hóa thành công trên dữ liệu mới!")
    print(f"=> Dữ liệu cuối cùng được lưu ở: {featured_output}")

if __name__ == '__main__':
    run_pipeline()
