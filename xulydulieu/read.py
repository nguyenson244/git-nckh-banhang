import pandas as pd
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
default_data_folder = os.path.join(parent_dir, 'data')

def doc_du_lieu(data_folder=default_data_folder):
    file_names = ['data_2023.csv', 'data_2024.csv', 'data_2025.csv']
    dfs = []
    
    for file_name in file_names:
        file_path = os.path.join(data_folder, file_name)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            dfs.append(df)
            print(f"Đã đọc file: {file_name}")
        else:
            print(f"Cảnh báo: Không tìm thấy file {file_path}")
            
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df
    else:
        print("Không có dữ liệu nào được đọc.")
        return pd.DataFrame()

if __name__ == "__main__":
    # Chạy thử hàm
    df_tong = doc_du_lieu()
    if not df_tong.empty:
        print("\nThông tin dữ liệu tổng hợp:")
        print(df_tong.info())
        
        # 1. Để in TOÀN BỘ dữ liệu ra màn hình console (có thể bị lag vì có hơn 21.000 dòng):
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # print(df_tong)
        
        # 2. Cách tốt hơn: Lưu toàn bộ dữ liệu ra một file CSV mới để dễ xem bằng Excel/ứng dụng khác
        output_file = os.path.join(current_dir, 'data_all.csv')
        df_tong.to_csv(output_file, index=False)
        print(f"\nĐã xuất toàn bộ dữ liệu ra file: {output_file}")
