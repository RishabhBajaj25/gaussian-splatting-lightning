import csv
import os.path as osp
import numpy as np
import subprocess

output_folder_path = '/media/rishabh/SSD_1/Data/Table_vid_reg/project_2_images'
path_2_trained_GS = '/home/rishabh/projects/gaussian-splatting/output/table_2/point_cloud/iteration_30000/500_test_point_cloud.ply'

..
def read_csv_transformations(csv_path, transform_key):
    with open(csv_path, mode='r') as file:
        reader = csv.reader(file)
        rows = list(reader)

        transform_matrix = None
        euler_angles = None

        for i, row in enumerate(rows):
            if row and row[0] == transform_key:
                matrix = [list(map(float, rows[i + j])) for j in range(1, 5)]
                transform_matrix = np.array(matrix)
            elif row and row[0] == "euler_angles_zyx":
                euler_angles = list(map(float, rows[i + 1]))
                break

        translations = transform_matrix[:3, 3] if transform_matrix is not None else [0, 0, 0]
        return translations, euler_angles


# Read global transformation parameters
global_translations, global_euler_zyx = read_csv_transformations(
    osp.join(output_folder_path, 'global_reg_result.csv'), "result_T_m2_m1"
)

# Read fine transformation parameters
fine_translations, fine_euler_zyx = read_csv_transformations(
    osp.join(output_folder_path, 'fine_reg_result.csv'), "icp_result.transformation"
)

# Read scale value
global_csv = osp.join(output_folder_path, 'global_reg_result.csv')
with open(global_csv, mode='r') as file:
    reader = csv.reader(file)
    rows = list(reader)
    for i, row in enumerate(rows):
        if row and row[0] == "scale":
            scale = float(rows[i + 1][0])
            break

# Apply scaling
input_ply = path_2_trained_GS
output_ply = input_ply.replace('.ply', '_scale.ply')
scale_command = f'python gaussian_transform.py {input_ply} {output_ply} --scale {scale}'
scale_result = subprocess.run(scale_command, shell=True, capture_output=True, text=True)
print("STDOUT:", scale_result.stdout)

# Apply global transformation
input_ply = output_ply
output_ply = input_ply.replace('.ply', '_global_reg.ply')
global_reg_command = (
    f'python gaussian_transform.py {input_ply} {output_ply} '
    f'--tx {global_translations[0]} --ty {global_translations[1]} --tz {global_translations[2]} '
    f'--rx {global_euler_zyx[2]} --ry {global_euler_zyx[1]} --rz {global_euler_zyx[0]}'
)
global_reg_result = subprocess.run(global_reg_command, shell=True, capture_output=True, text=True)
print("STDOUT:", global_reg_result.stdout)

# Apply fine transformation
input_ply = output_ply
output_ply = input_ply.replace('.ply', '_icp.ply')
fine_reg_command = (
    f'python gaussian_transform.py {input_ply} {output_ply} '
    f'--tx {fine_translations[0]} --ty {fine_translations[1]} --tz {fine_translations[2]} '
    f'--rx {fine_euler_zyx[2]} --ry {fine_euler_zyx[1]} --rz {fine_euler_zyx[0]}'
)
fine_reg_result = subprocess.run(fine_reg_command, shell=True, capture_output=True, text=True)
print("STDOUT:", fine_reg_result.stdout)

print("Yay")
