# backend/convert_to_md.py convert_to_md.py (güncel ve güvenli hali) backend/scripts/convert_to_md.sh script tarafında kullanılan kod
import os
import shutil
import sys

def convert_py_to_md(src_dir, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith('.')]

        rel_path = os.path.relpath(root, src_dir)
        dst_path = os.path.join(dst_dir, rel_path)
        os.makedirs(dst_path, exist_ok=True)

        for file in files:
            if file.endswith(('.py', '.js', '.jsx', '.css')):
                src_file_path = os.path.join(root, file)
                new_filename = os.path.splitext(file)[0] + '.md'
                dst_file_path = os.path.join(dst_path, new_filename)
                try:
                    shutil.copyfile(src_file_path, dst_file_path)
                except Exception as e:
                    print(f"❌ {src_file_path} kopyalanamadı: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Kullanım: python convert_to_md.py <kaynak_klasör> <hedef_klasör>")
        sys.exit(1)

    convert_py_to_md(sys.argv[1], sys.argv[2])
