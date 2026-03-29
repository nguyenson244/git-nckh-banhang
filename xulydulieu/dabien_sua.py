import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def phan_tich_da_bien(file_path):
    print(f"Đang đọc dữ liệu từ: {file_path}")
    df = pd.read_csv(file_path)
    
    output_dir = os.path.dirname(file_path)
    charts_dir = os.path.join(output_dir, 'bieu_do_da_bien_sua')
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
        
    sns.set_theme(style="whitegrid")
    
    print("1. Đang vẽ biểu đồ Total QTY Boxplot theo BRAND...")
    if 'Total QTY' in df.columns and 'BRAND' in df.columns:
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, x='BRAND', y='Total QTY', palette='Set2')
        plt.title('Sự phân tán của biến Total QTY theo Từng Thương hiệu')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'box_qty_theo_brand.png'))
        plt.close()
        
    print("2. Đang vẽ biểu đồ Đường (Time-series) của Total QTY theo thời gian...")
    if 'ACTUALSHIPDATE' in df.columns and 'Total QTY' in df.columns:
        df['ACTUALSHIPDATE'] = pd.to_datetime(df['ACTUALSHIPDATE'])
        daily_qty = df.groupby('ACTUALSHIPDATE')['Total QTY'].sum().reset_index()
        
        plt.figure(figsize=(14, 5))
        sns.lineplot(data=daily_qty, x='ACTUALSHIPDATE', y='Total QTY', color='coral', marker='o')
        plt.title('Xu hướng Biến động Tổng lượng hàng (Total QTY) theo Thời gian')
        plt.xlabel('Ngày giao hàng')
        plt.ylabel('Tổng Total QTY')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'line_qty_over_time.png'))
        plt.close()

    print("3. Đang vẽ Ma trận tương quan (Correlation Heatmap)...")
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if len(num_cols) > 1:
        corr_matrix = df[num_cols].corr()
        plt.figure(figsize=(12, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
        plt.title('Ma trận Tương quan (Correlation Heatmap)')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'heatmap_correlation.png'))
        plt.close()
        
    print(f"\n=> Đã vẽ xong các biểu đồ Đa biến! Dữ liệu nằm trong thư mục: {charts_dir}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, 'data_processed_sua.csv')
    if os.path.exists(input_file):
        phan_tich_da_bien(input_file)
    else:
        print(f"Không tìm thấy file {input_file}")
