import os
from PIL import Image
import sys


def convert_images_to_webp():
    input_folder = 'input'
    output_folder = 'output'

    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"エラー: '{input_folder}' フォルダが存在しません。")
        sys.exit(1)

    # outputフォルダを綺麗にする（中身を全削除）
    import shutil

    if os.path.exists(output_folder):
        for root, dirs, files in os.walk(output_folder, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))
        print(f"出力フォルダ '{output_folder}' の中身を削除しました。")
    # Create output folder if it doesn't exist
    try:
        os.makedirs(output_folder, exist_ok=True)
        print(f"出力フォルダ '{output_folder}' を確認しました。")
    except OSError as e:
        print(f'エラー: 出力フォルダの作成に失敗しました: {e}')
        sys.exit(1)

    # 画像ファイルとその他ファイルを分けて処理
    supported_extensions = ('.jpg', '.jpeg', '.png')
    image_files = []
    other_files = []

    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            input_path = os.path.join(root, filename)
            rel_path = os.path.relpath(input_path, input_folder)
            if filename.lower().endswith(supported_extensions):
                image_files.append((input_path, rel_path))
            else:
                other_files.append((input_path, rel_path))

    if not image_files and not other_files:
        print('変換・コピー対象のファイルが見つかりませんでした。')
        return

    print(f'変換対象ファイル数: {len(image_files)}')
    print(f'コピー対象ファイル数: {len(other_files)}')
    successful_conversions = 0
    failed_conversions = 0
    successful_copies = 0
    failed_copies = 0

    # 画像変換
    for i, (input_path, rel_path) in enumerate(image_files, 1):
        name_without_ext = os.path.splitext(rel_path)[0]
        output_rel_path = f'{name_without_ext}.webp'
        output_path = os.path.join(output_folder, output_rel_path)
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        print(f'[{i}/{len(image_files)}] 変換中: {input_path} → {output_path}')
        try:
            with Image.open(input_path) as img:
                if img.mode == 'RGBA' and input_path.lower().endswith(
                    ('.jpg', '.jpeg')
                ):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                img.save(output_path, 'WEBP', quality=95, lossless=False)
                successful_conversions += 1
                print(f'  → 完了: {output_rel_path}')
        except Exception as e:
            print(f'  → エラー: {input_path} の変換に失敗しました - {e}')
            failed_conversions += 1

    # その他ファイルのコピー
    for i, (input_path, rel_path) in enumerate(other_files, 1):
        output_path = os.path.join(output_folder, rel_path)
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        print(f'[copy {i}/{len(other_files)}] コピー中:')
        print(f'  {input_path} → {output_path}')
        try:
            shutil.copy2(input_path, output_path)
            successful_copies += 1
            print(f'  → 完了: {rel_path}')
        except Exception as e:
            print(f'  → エラー: {input_path} のコピーに失敗しました - {e}')
            failed_copies += 1

    # 変換前後の合計ファイルサイズを計算
    def get_total_size(folder, exts):
        total = 0
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(exts):
                    total += os.path.getsize(os.path.join(root, file))
        return total

    before_size = get_total_size(input_folder, supported_extensions)
    after_size = get_total_size(output_folder, ('.webp',))

    print('\n' + '=' * 50)
    print('変換・コピー処理完了')
    print(
        f'画像変換 成功: {successful_conversions}件 / 失敗: {failed_conversions}件'
    )
    print(
        f'ファイルコピー 成功: {successful_copies}件 / 失敗: {failed_copies}件'
    )
    print('=' * 50)
    print(f'変換前合計サイズ: {before_size / 1024:.2f} KB')
    print(f'変換後合計サイズ: {after_size / 1024:.2f} KB')
    if before_size > 0:
        reduction = (before_size - after_size) / before_size * 100
        print(f'容量削減率: {reduction:.2f}%')
    else:
        print('容量削減率: 計算不可（変換前サイズが0）')


if __name__ == '__main__':
    convert_images_to_webp()
