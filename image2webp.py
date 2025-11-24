# ------------------------------------------------------------
# WebP 画像変換ツール – 使い方チートシート
# ------------------------------------------------------------
#
# 【基本コマンド】
#     python3 image2webp.py
#
#     input/ フォルダ内の画像を WebP へ変換し、
#     output/ フォルダに保存します。
#     ※実行前に output/ の中身は毎回すべて削除されます。
#
#
# 【品質（quality）を指定 0〜100】
# ・軽量化優先（推奨）
#     python3 image2webp.py --quality 80
#
# ・高品質
#     python3 image2webp.py --quality 95
#
#
# 【圧縮方法（method：0〜6）】
# ・高速変換
#     python3 image2webp.py --method 0
#
# ・高圧縮（最も小さくしたい）
#     python3 image2webp.py --method 6
#
#
# 【ロスレス（PNG のように劣化なし）】
# ・完全ロスレス
#     python3 image2webp.py --lossless
#
# ・品質指定＋ロスレス（最大画質）
#     python3 image2webp.py --lossless --quality 100
#
#
# 【組み合わせ例】
# ・軽くてキレイのバランス
#     python3 image2webp.py --quality 85 --method 4
#
# ・最大圧縮（サイズ最小）
#     python3 image2webp.py --quality 80 --method 6
#
# ・PNG 代替（透明保持・完全ロスレス）
#     python3 image2webp.py --lossless
#
#
# 【注意点】
# ・input/ と output/ のフォルダ名は固定
# ・output/ は実行ごとに空にされる仕様
# ・画像以外のファイル（例: .DS_Store）はコピーされます
# ・巨大画像は警告が出る場合があるため必要なら:
#       from PIL import Image
#       Image.MAX_IMAGE_PIXELS = None
#   を冒頭に追加してください
#
# ------------------------------------------------------------

import os
import sys
import argparse
from PIL import Image
import shutil


def convert_images_to_webp(quality, method, lossless):
    input_folder = 'input'
    output_folder = 'output'

    # Check input folder
    if not os.path.exists(input_folder):
        print(f"エラー: '{input_folder}' フォルダが存在しません。")
        sys.exit(1)

    # Clean output folder
    if os.path.exists(output_folder):
        for root, dirs, files in os.walk(output_folder, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))
        print(f"出力フォルダ '{output_folder}' の中身を削除しました。")

    os.makedirs(output_folder, exist_ok=True)
    print(f"出力フォルダ '{output_folder}' を確認しました。")

    supported_extensions = ('.jpg', '.jpeg', '.png')
    image_files = []
    other_files = []

    # Collect files
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

    # Convert images
    for i, (input_path, rel_path) in enumerate(image_files, 1):
        name_without_ext = os.path.splitext(rel_path)[0]
        output_rel_path = f'{name_without_ext}.webp'
        output_path = os.path.join(output_folder, output_rel_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        print(f'[{i}/{len(image_files)}] 変換中: {input_path} → {output_path}')

        try:
            with Image.open(input_path) as img:
                # JPG+アルファ → 白背景に合成
                if img.mode == 'RGBA' and input_path.lower().endswith(('.jpg', '.jpeg')):
                    bg = Image.new('RGB', img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg

                # Save WebP with options
                img.save(
                    output_path,
                    'WEBP',
                    quality=quality,
                    lossless=lossless,
                    method=method
                )
                successful_conversions += 1
                print(f'  → 完了: {output_rel_path}')

        except Exception as e:
            print(f'  → エラー: {input_path} の変換に失敗 - {e}')
            failed_conversions += 1

    # Copy other files
    for i, (input_path, rel_path) in enumerate(other_files, 1):
        output_path = os.path.join(output_folder, rel_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f'[copy {i}/{len(other_files)}] コピー中:')
        print(f'  {input_path} → {output_path}')
        try:
            shutil.copy2(input_path, output_path)
            successful_copies += 1
            print(f'  → 完了: {rel_path}')
        except Exception as e:
            print(f'  → エラー: {input_path} のコピーに失敗 - {e}')
            failed_copies += 1

    # Size calc
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
    print(f'画像変換 成功: {successful_conversions}件 / 失敗: {failed_conversions}件')
    print(f'ファイルコピー 成功: {successful_copies}件 / 失敗: {failed_copies}件')
    print('=' * 50)
    print(f'変換前合計サイズ: {before_size / 1024:.2f} KB')
    print(f'変換後合計サイズ: {after_size / 1024:.2f} KB')

    if before_size > 0:
        reduction = (before_size - after_size) / before_size * 100
        print(f'容量削減率: {reduction:.2f}%')
    else:
        print('容量削減率: 計算不可（変換前サイズが0）')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='画像を WebP に変換するツール')

    parser.add_argument('--quality', type=int, default=95,
                        help='WebP 品質（0〜100）')
    parser.add_argument('--method', type=int, default=4,
                        help='圧縮方法（0〜6, 値が大きいほど高圧縮）')
    parser.add_argument('--lossless', action='store_true',
                        help='ロスレス WebP を有効化')

    args = parser.parse_args()

    convert_images_to_webp(
        quality=args.quality,
        method=args.method,
        lossless=args.lossless
    )