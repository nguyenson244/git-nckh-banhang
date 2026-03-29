import pandas as pd
import numpy as np
import os

def xay_dung_dac_trung(file_path):
    print(f"Đang đọc dữ liệu gốc từ: {file_path}")
    df = pd.read_csv(file_path)
    
    # Đảm bảo cột thời gian đúng định dạng, loại bỏ lỗi
    if 'ACTUALSHIPDATE' in df.columns:
        df['ACTUALSHIPDATE'] = pd.to_datetime(df['ACTUALSHIPDATE'], errors='coerce')
        # Sắp xếp thời gian để dễ tính toán Lag / Thay đổi
        df = df.sort_values(by=['BRAND', 'ACTUALSHIPDATE']).reset_index(drop=True)

    print("\n--- BẮT ĐẦU FEATURE ENGINEERING (TRÍCH XUẤT ĐẶC TRƯNG) ---")

    # -------------------------------------------------------------
    # NHÓM ĐẶC TRƯNG 1: MÙA VỤ & THỜI GIAN (Seasonality & Time)
    # -------------------------------------------------------------
    # (Dựa trên nhận xét: Có chu kỳ đáy vào Q1 và đỉnh vào Q3)
    print("1. Đang tạo đặc trưng về Thời gian (Tháng, Quý, Cao điểm)...")
    if 'ACTUALSHIPDATE' in df.columns:
        df['Month'] = df['ACTUALSHIPDATE'].dt.month
        df['Quarter'] = df['ACTUALSHIPDATE'].dt.quarter
        df['DayOfWeek'] = df['ACTUALSHIPDATE'].dt.dayofweek # Thứ 2 là 0, CN là 6
        
        # Đặc trưng 1: Is_Weekend (Cuối tuần - T7/CN)
        df['Is_Weekend'] = df['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)
        
        # Đặc trưng 2: Is_High_Season (Mùa vụ cao điểm: Tháng 6, 7, 8 theo phân tích Đa biến)
        df['Is_High_Season'] = df['Month'].apply(lambda x: 1 if x in [6, 7, 8] else 0)
        
        # Đặc trưng 3: Is_Low_Season (Mùa vụ thấp điểm: Tháng 1, 2, 3, 4)
        df['Is_Low_Season'] = df['Month'].apply(lambda x: 1 if x in [1, 2, 3, 4] else 0)

    # -------------------------------------------------------------
    # NHÓM ĐẶC TRƯNG 2: RỦI RO ĐỘT BIẾN THEO NHÃN HIỆU (Brands)
    # -------------------------------------------------------------
    # (Dựa trên nhận xét: BREAD là bán sỉ cực tốt, CAKE và BISCUIT toàn Outliers/ngoại lai)
    print("2. Đang tạo đặc trưng Tình trạng Thương hiệu...")
    if 'BRAND' in df.columns:
        # One-hot encoding nhãn bánh mì tươi (Mặt hàng chủ lực bán lưu lượng khổng lồ)
        df['Is_Bread_Product'] = df['BRAND'].apply(lambda x: 1 if 'BREAD' in str(x).upper() else 0)
        
        # Flag các nhãn có rủi ro đặt đơn đột biến (Outlier rủi ro)
        df['Risk_Outlier_Brand'] = df['BRAND'].apply(lambda x: 1 if any(word in str(x).upper() for word in ['CAKE', 'BISCUIT']) else 0)

    # -------------------------------------------------------------
    # NHÓM ĐẶC TRƯNG 3: TƯƠNG QUAN LƯỢNG VÀ THỂ TÍCH (Volume Interaction)
    # -------------------------------------------------------------
    # (Dựa trên nhận xét: Scatter Plot loe dần, không hoàn toàn đồng dạng)
    print("3. Đang tạo đặc trưng Tương tác Thể tích - Sản lượng...")
    if 'Total QTY' in df.columns and 'Total CBM' in df.columns:
        # Đặc trưng sức kết hợp: Tổng mức luân chuyển
        df['QTY_CBM_Interact'] = df['Total QTY'] * df['Total CBM']
        
        # Đặc trưng "Sự hao hụt Không gian": Chênh lệch QTY CBM
        df['Space_Loss_Factor'] = df['Total QTY'] - df['Total CBM']

    # -------------------------------------------------------------
    # NHÓM ĐẶC TRƯNG 4: CHUỖI THỜI GIAN THEO BRAND (Rolling Lags)
    # -------------------------------------------------------------
    # Dự đoán mô hình phải cần lịch sử doanh số của chính BRAND đó trong 3-7 ngày trước
    print("4. Đang tạo đặc trưng Trượt quá khứ (Rolling Lags) để dò xu hướng...")
    if 'BRAND' in df.columns and 'Total QTY' in df.columns and 'ACTUALSHIPDATE' in df.columns:
        # Tính Trung bình 7 ngày trước đó của Sản lượng (Rolling Mean) để lấy đà bán
        df['QTY_Rolling_7_Days'] = df.groupby('BRAND')['Total QTY'].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
        # Tính Lệch chuẩn để xem độ bất ổn (Outlier check) của 7 ngày đó
        df['QTY_Std_7_Days']   = df.groupby('BRAND')['Total QTY'].transform(lambda x: x.rolling(window=7, min_periods=1).std())

    # -------------------------------------------------------------
    # KIỂM TRA & LƯU LẠI
    # -------------------------------------------------------------
    # Thay thế các NaN do phép chia, std sinh ra bằng 0
    df = df.fillna(0)
    
    print("\n--- ĐẶC TRƯNG VỪA ĐƯỢC THÊM ---")
    new_cols = ['Month', 'Quarter', 'Is_Weekend', 'Is_High_Season', 'Is_Low_Season', 
                'Is_Bread_Product', 'Risk_Outlier_Brand', 'QTY_CBM_Interact', 'Space_Loss_Factor',
                'QTY_Rolling_7_Days', 'QTY_Std_7_Days']
    # Chỉ in những cột tạo thành công
    created_cols = [c for c in new_cols if c in df.columns]
    print(df[created_cols].head())
    
    # Lưu ra file CSV mới
    output_dir = os.path.dirname(file_path)
    output_file = os.path.join(output_dir, 'data_featured_sua.csv')
    df.to_csv(output_file, index=False)
    
    print(f"\n=> 11 Cột Đặc trưng (Features) mới đã được kỹ sư hóa thành công!")
    print(f"=> Dữ liệu cuối cùng được lưu ở: {output_file}")


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, 'data_processed_sua.csv')
    
    if os.path.exists(input_file):
        xay_dung_dac_trung(input_file)
    else:
        print(f"LỖI: Không tìm thấy file {input_file}.")
