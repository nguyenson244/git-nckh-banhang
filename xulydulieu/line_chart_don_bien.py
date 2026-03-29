import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def ve_bieu_do_duong_hang_ngay(file_path):
    print(f"Đang đọc dữ liệu từ: {file_path}")
    df = pd.read_csv(file_path)
    
    # Đảm bảo thư mục đích tồn tại
    output_dir = os.path.dirname(file_path)
    charts_dir = os.path.join(output_dir, 'bieu_do_don_bien')
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
        
    print("\nĐang xử lý dữ liệu thời gian...")
    # Chuyển đổi sang định dạng Datetime
    if 'ACTUALSHIPDATE' in df.columns and 'Total QTY' in df.columns:
        df['ACTUALSHIPDATE'] = pd.to_datetime(df['ACTUALSHIPDATE'], errors='coerce')
        # Bỏ các dòng rỗng ngày tháng
        df = df.dropna(subset=['ACTUALSHIPDATE'])
        
        # Gom nhóm và tính Tổng sản lượng (QTY) được bán ra theo từng NGÀY
        # (Tại đây data_processed.csv đã là dữ liệu lọc riêng của Kinh Đô)
        daily_sales = df.groupby(df['ACTUALSHIPDATE'].dt.date)['Total QTY'].sum().reset_index()
        
        print(f"Đã gom nhóm thành công {len(daily_sales)} ngày bán hàng.")
        
        # Thiết lập biểu đồ
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(15, 6))
        
        # Vẽ biểu đồ đường
        sns.lineplot(data=daily_sales, x='ACTUALSHIPDATE', y='Total QTY', color='blue', linewidth=1.5)
        
        plt.title('Sản lượng Hàng hóa Kinh Đô bán ra theo Từng Ngày (Daily Sales)', fontsize=14, fontweight='bold')
        plt.xlabel('Ngày giao hàng (Actual Ship Date)', fontsize=12)
        plt.ylabel('Tổng sản lượng (Total QTY - Chuẩn hóa)', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Lưu file riêng vào folder bieu_do_don_bien
        save_path = os.path.join(charts_dir, 'line_daily_kinhdo.png')
        plt.savefig(save_path)
        plt.close()
        
        print(f"\n=> Vẽ thành công! Biểu đồ đã được lưu tại: {save_path}")
    else:
        print("LỖI: Không tìm thấy cột ACTUALSHIPDATE hoặc Total QTY trong dữ liệu.")                 

if __name__ == "__main__":
    # Dùng file gốc đã qua xử lý
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, 'data_processed_sua.csv')
    if os.path.exists(input_file):
        ve_bieu_do_duong_hang_ngay(input_file)
    else:
        print(f"Không tìm thấy file {input_file}!")
