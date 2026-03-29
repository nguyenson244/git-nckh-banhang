import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def phan_tich_hai_bien(file_path):
    print(f"Đang đọc dữ liệu từ: {file_path}")
    df = pd.read_csv(file_path)
    
    output_dir = os.path.dirname(file_path)
    charts_dir = os.path.join(output_dir, 'bieu_do_hai_bien_sua')
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
        
    sns.set_theme(style="whitegrid")
    
    print("\n--- BẮT ĐẦU PHÂN TÍCH 2 BIẾN (BIVARIATE ANALYSIS) ---")

    print("1. Đang vẽ Scatter Plot (Biểu đồ phân tán): Total QTY vs Total CBM...")
    if 'Total QTY' in df.columns and 'Total CBM' in df.columns:
        plt.figure(figsize=(10, 6))
        sns.regplot(data=df, x='Total QTY', y='Total CBM', scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
        plt.title('Tương quan tuyến tính: Thể tích (CBM) theo Khối lượng (QTY)')
        plt.xlabel('Total QTY (Chuẩn hóa)')
        plt.ylabel('Total CBM (Chuẩn hóa)')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, '1_scatter_qty_vs_cbm.png'))
        plt.close()

    print("2. Đang vẽ Boxplot (Biểu đồ hộp): BRAND vs Total QTY...")
    if 'BRAND' in df.columns and 'Total QTY' in df.columns:
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, x='BRAND', y='Total QTY', palette='Set2')
        plt.title('Phân phối và khoảng Ngoại lai (Outliers) của QTY theo Thương hiệu')
        plt.xlabel('Thương hiệu (BRAND)')
        plt.ylabel('Sản lượng (Total QTY)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, '2_boxplot_brand_vs_qty.png'))
        plt.close()

    print("2b. Đang vẽ Barplot (Trung bình QTY theo Category)...")
    if 'CATEGORY' in df.columns and 'Total QTY' in df.columns:
        plt.figure(figsize=(8, 5))
        sns.barplot(data=df, x='CATEGORY', y='Total QTY', estimator='mean', errorbar=None, palette='pastel')
        plt.title('Trung bình Lượng hàng hóa theo Phân loại (CATEGORY)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, '2_barplot_category_vs_qty_mean.png'))
        plt.close()

    print("3. Đang vẽ Grouped Bar/Heatmap: BRAND vs CATEGORY/Week...")
    if 'BRAND' in df.columns and 'Week' in df.columns:
        plt.figure(figsize=(16, 6))
        sns.countplot(data=df, x='Week', hue='BRAND', palette='Set1')
        plt.title('Số lượng đơn hàng phân bổ theo thứ trong tuần cho từng Thương hiệu')
        plt.xlabel('Ngày trong tuần (Week)')
        plt.ylabel('Số lượng đơn (Số dòng dữ liệu)')
        plt.xticks(rotation=45)
        plt.legend(title='Nhãn hiệu', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, '3_countplot_week_vs_brand.png'))
        plt.close()

    print("4. Đang vẽ Line plot (Biểu đồ đường): Thời gian vs Total QTY...")
    if 'ACTUALSHIPDATE' in df.columns and 'Total QTY' in df.columns:
        df['ACTUALSHIPDATE'] = pd.to_datetime(df['ACTUALSHIPDATE'], errors='coerce')
        df_time = df.dropna(subset=['ACTUALSHIPDATE'])
        df_time['MonthLabel'] = df_time['ACTUALSHIPDATE'].dt.to_period('M')
        monthly_qty = df_time.groupby('MonthLabel')['Total QTY'].sum().reset_index()
        monthly_qty['MonthLabel'] = monthly_qty['MonthLabel'].astype(str)

        plt.figure(figsize=(14, 5))
        sns.lineplot(data=monthly_qty, x='MonthLabel', y='Total QTY', color='purple', marker='o')
        plt.title('Tổng sản lượng vận chuyển theo từng tháng (Chu kỳ 2023 - 2025)')
        plt.xlabel('Tháng xuất hàng')
        plt.ylabel('Tổng Lượng hàng (Total QTY)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, '4_lineplot_time_vs_qty.png'))
        plt.close()
        
    print(f"\n=> Đã xử lý xong Phân tích 2 biến! Tất cả ảnh biểu đồ đã lưu ở folder: {charts_dir}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, 'data_processed_sua.csv')
    
    if os.path.exists(input_file):
        phan_tich_hai_bien(input_file)
    else:
        print(f"LỖI: Không tìm thấy file {input_file}.")
