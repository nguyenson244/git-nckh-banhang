import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Ensure UTF-8 output for Vietnamese characters
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def phan_tich_don_bien(file_path):
    print(f"Đang đọc dữ liệu từ: {file_path}")
    df = pd.read_csv(file_path)
    
    output_dir = os.path.dirname(file_path)
    charts_dir = os.path.join(output_dir, 'bieu_do_don_bien_sua')
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
        
    print(f"Số lượng dòng dữ liệu sau khi sửa lõi (không lọc): {df.shape[0]}")
    sns.set_theme(style="whitegrid")
    
    num_cols = ['Total QTY', 'Total CBM']
    for col in num_cols:
        if col in df.columns:
            plt.figure(figsize=(10, 6))
            sns.histplot(df[col], kde=True, bins=50, color='skyblue')
            plt.title(f'Phân phối của {col}')
            plt.xlabel(col)
            plt.ylabel('Tần suất')
            
            save_path = os.path.join(charts_dir, f'hist_{col.replace(" ", "_").lower()}.png')
            plt.savefig(save_path)
            plt.close()
            print(f"- Đã lưu biểu đồ phân phối: {save_path}")
            
    for col in num_cols:
        if col in df.columns:
            plt.figure(figsize=(10, 4))
            sns.boxplot(x=df[col], color='lightgreen')
            plt.title(f'Boxplot của {col}')
            
            save_path = os.path.join(charts_dir, f'box_{col.replace(" ", "_").lower()}.png')
            plt.savefig(save_path)
            plt.close()
            print(f"- Đã lưu biểu đồ boxplot: {save_path}")
            
    cat_cols = ['CATEGORY', 'WHSEID', 'BRAND', 'Week']
    for col in cat_cols:
        if col in df.columns:
            plt.figure(figsize=(12, 6))
            order = df[col].value_counts().index
            sns.countplot(data=df, x=col, order=order, palette='viridis', hue=col, legend=False)
            
            plt.title(f'Số lượng giao dịch theo {col}')
            plt.xlabel(col)
            plt.ylabel('Số lượng')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            save_path = os.path.join(charts_dir, f'bar_{col.lower()}.png')
            plt.savefig(save_path)
            plt.close()
            print(f"- Đã lưu biểu đồ đếm số lượng: {save_path}")

    print("\n=> THỐNG KÊ MÔ TẢ CƠ BẢN CÁC BIẾN SỐ:")
    print(df[num_cols].describe().round(2))

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, 'data_processed_sua.csv')
    
    if os.path.exists(input_file):
        phan_tich_don_bien(input_file)
        print("\n=> Hoàn tất phân tích đơn biến! Các biểu đồ đã được lưu trong thư mục 'bieu_do_don_bien_sua'.")
    else:
        print(f"Không tìm thấy file {input_file}.")
