import requests
import re
import os
import sys
from tqdm import tqdm
import urllib.parse
import subprocess # 导入 subprocess 模块
try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    print("警告：未安装 mutagen 库，无法添加MP3元数据。运行 'pip install mutagen' 来安装。")

def sanitize_filename(filename):
    """
    Sanitizes a string to be a valid filename.
    Removes invalid characters and shortens it if too long.
    """
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename) # Replace invalid characters with underscore
    filename = filename.strip() # Remove leading/trailing whitespace
    if len(filename) > 200: # Limit filename length
        filename = filename[:200]
    return filename

def download_file(url, filename, output_dir, description, referer=None):
    """
    Downloads a file from a URL with a progress bar.
    Returns True on success, False on failure.
    """
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    print(f"\n[{description}] 开始下载: {filepath}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        if referer:
            headers['Referer'] = referer

        response = requests.get(url, stream=True, headers=headers, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 # 1 KB

        with open(filepath, 'wb') as f:
            for data in tqdm(response.iter_content(block_size),
                             total=(total_size // block_size) + 1,
                             unit='KB',
                             unit_scale=True,
                             desc=f"下载 {description}"):
                f.write(data)
        print(f"[{description}] 下载完成: {filepath}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[{description}] 下载失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Server response (if available): {e.response.text}")
        return False
    except Exception as e:
        print(f"[{description}] 发生未知错误: {e}")
        return False

# 新的转换函数，使用 subprocess 调用 FFmpeg
def convert_m4a_to_mp3_ffmpeg_cli(m4a_filepath, mp3_filepath, bitrate="192k"):
    """
    Converts an M4A audio file to MP3 format using FFmpeg via command line.
    Requires FFmpeg to be installed and in system PATH.
    """
    print(f"\n[音频转换] 正在将 {os.path.basename(m4a_filepath)} 转换为 MP3...")
    # FFmpeg 命令：
    # -i <input_file>：输入文件
    # -vn：不包含视频流（只处理音频）
    # -ar 44100：设置音频采样率（例如 44.1kHz）
    # -ac 2：设置音频通道数（2为立体声）
    # -b:a <bitrate>：设置音频比特率
    # <output_file>：输出文件
    command = [
        'ffmpeg',
        '-i', m4a_filepath,
        '-vn',             # Disable video
        '-ar', '44100',    # Audio sample rate
        '-ac', '2',        # Audio channels (stereo)
        '-b:a', bitrate,   # Audio bitrate
        mp3_filepath
    ]
    try:
        # 使用 subprocess.run 执行命令
        # capture_output=True: 捕获标准输出和标准错误
        # text=True: 将输出解码为文本
        # check=True: 如果命令返回非零退出代码，则抛出 CalledProcessError
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"[音频转换] 转换成功: {os.path.basename(mp3_filepath)}")
        # print("FFmpeg stdout:\n", result.stdout) # 调试时可以打印 FFmpeg 输出
        # print("FFmpeg stderr:\n", result.stderr)
        return True
    except FileNotFoundError:
        print(f"[音频转换] 错误：FFmpeg 未找到。请确保 FFmpeg 已安装并添加到系统 PATH。")
        print("请检查你的FFmpeg安装以及PATH环境变量设置。")
        return False
    except subprocess.CalledProcessError as e:
        print(f"[音频转换] FFmpeg 转换失败，错误代码: {e.returncode}")
        print(f"FFmpeg stdout:\n{e.stdout}")
        print(f"FFmpeg stderr:\n{e.stderr}")
        print("请检查输入文件是否损坏或FFmpeg命令是否存在问题。")
        return False
    except Exception as e:
        print(f"[音频转换] 发生未知错误: {e}")
        return False

def add_metadata_to_mp3(mp3_filepath, cover_filepath, title, artist="", album="", year=""):
    """
    Adds metadata and cover art to an MP3 file using mutagen.
    """
    if not MUTAGEN_AVAILABLE:
        print("[元数据] 无法添加元数据，因为 mutagen 库未安装。")
        return False
    
    try:
        print(f"[元数据] 正在为 {os.path.basename(mp3_filepath)} 添加元数据...")
        print(f"[元数据] 设置标题为: {title}")
        
        # 加载MP3文件
        audio = MP3(mp3_filepath, ID3=ID3)
        
        # 添加或更新ID3标签
        if audio.tags is None:
            audio.add_tags()
        
        # 添加标题
        audio.tags.add(TIT2(encoding=3, text=title))
        
        # 添加艺术家（如果提供）
        if artist:
            audio.tags.add(TPE1(encoding=3, text=artist))
        
        # 添加专辑（如果提供）
        if album:
            audio.tags.add(TALB(encoding=3, text=album))
        
        # 添加年份（如果提供）
        if year:
            audio.tags.add(TDRC(encoding=3, text=year))
        
        # 添加封面图片
        if cover_filepath and os.path.exists(cover_filepath):
            with open(cover_filepath, 'rb') as cover_file:
                cover_data = cover_file.read()
                
            audio.tags.add(APIC(
                encoding=3,  # UTF-8
                mime='image/jpeg',  # JPEG图片
                type=3,  # 封面图片
                desc='Cover',
                data=cover_data
            ))
            print(f"[元数据] 已添加封面图片")
        
        # 保存更改
        audio.save()
        print(f"[元数据] 元数据添加成功")
        return True
        
    except Exception as e:
        print(f"[元数据] 添加元数据失败: {e}")
        return False

def get_user_metadata(final_title=None):
    """
    询问用户是否要添加/修改元数据，并获取元数据信息
    """
    add_metadata = input("是否要添加/修改MP3文件的元数据？(y/n): ").lower().strip()
    if add_metadata != 'y':
        return None
    
    if final_title:
        print(f"\n当前文件标题将设置为: {final_title}")
    print("\n请输入元数据信息（直接按回车跳过）:")
    artist = input("艺术家/UP主: ").strip()
    album = input("专辑名称: ").strip()
    year = input("年份: ").strip()
    
    return {
        'artist': artist,
        'album': album,
        'year': year
    }

def rename_mp3_file(original_filepath, title):
    """
    询问用户是否要重命名MP3文件，并执行重命名
    """
    rename_file = input("是否要重命名MP3文件？(y/n): ").lower().strip()
    if rename_file != 'y':
        return original_filepath
    
    current_name = os.path.basename(original_filepath)
    print(f"当前文件名: {current_name}")
    
    # 提供默认的新文件名（基于视频标题）
    default_name = f"{sanitize_filename(title)}.mp3"
    new_name = input(f"请输入新的文件名（默认: {default_name}）: ").strip()
    
    if not new_name:
        new_name = default_name
    
    # 确保文件名以.mp3结尾
    if not new_name.lower().endswith('.mp3'):
        new_name += '.mp3'
    
    new_name = sanitize_filename(new_name)
    new_filepath = os.path.join(os.path.dirname(original_filepath), new_name)
    
    try:
        os.rename(original_filepath, new_filepath)
        print(f"文件已重命名为: {new_name}")
        return new_filepath
    except OSError as e:
        print(f"重命名失败: {e}")
        return original_filepath

def get_bvid_from_url(url):
    """
    Extracts BVid from a Bilibili URL.
    """
    match = re.search(r"BV([0-9a-zA-Z]{10})", url)
    if match:
        return match.group(0)
    return None

def main():
    while True:
        video_url = input("请输入Bilibili视频的URL (例如: https://www.bilibili.com/video/BV1k6AheoEmc/) 或输入 'q' 退出: ").strip()

        if video_url.lower() == 'q':
            print("退出程序。")
            break

        bvid = get_bvid_from_url(video_url)
        if not bvid:
            print("无效的Bilibili视频URL，请确保URL中包含BV号。")
            continue

        print(f"检测到BV号: {bvid}")

        common_referer = f"https://www.bilibili.com/video/{bvid}/"

        # 1. 获取视频信息 (封面URL, 标题, cid)
        view_api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        print(f"正在获取视频信息: {view_api_url}")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            response = requests.get(view_api_url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data['code'] != 0:
                print(f"获取视频信息失败: {data['message']}")
                continue

            video_info = data['data']
            video_title = sanitize_filename(video_info.get('title', bvid))
            cover_url = video_info.get('pic')
            cid = video_info.get('cid')

            if not cover_url or not cid:
                print("无法获取视频封面URL或CID。")
                continue

            output_folder = os.path.join("BiliDownloads", video_title)
            os.makedirs(output_folder, exist_ok=True)

            print(f"视频标题: {video_title}")
            print(f"封面URL: {cover_url}")
            print(f"视频CID: {cid}")

            # 2. 下载视频封面
            cover_filename = f"{video_title}_cover.jpg"
            download_file(cover_url, cover_filename, output_folder, "视频封面", referer=common_referer)

            # 3. 获取视频音频流URL
            playurl_api_url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&fnval=16"
            print(f"\n正在获取音频流信息: {playurl_api_url}")
            response = requests.get(playurl_api_url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data['code'] != 0:
                print(f"获取播放地址失败: {data['message']}")
                print("注意：对于部分视频，B站可能需要登录或WBI签名才能获取播放地址。此脚本仅支持无需特殊权限的视频。")
                continue

            dash_info = data['data'].get('dash')
            if not dash_info or not dash_info.get('audio'):
                print("无法获取DASH音频流信息，可能该视频不支持DASH或需要更高权限。")
                continue

            audio_streams = dash_info['audio']
            audio_streams.sort(key=lambda x: x.get('bandwidth', 0), reverse=True)

            audio_url = None
            if audio_streams:
                audio_url = audio_streams[0].get('base_url')

            if not audio_url:
                print("未找到可用的音频流URL。")
                continue

            m4a_filename = f"{video_title}_audio.m4a"
            print(f"音频流URL: {audio_url}")

            # 4. 下载视频音频 (m4a格式)
            audio_download_success = download_file(audio_url, m4a_filename, output_folder, "视频音频", referer=common_referer)

            # 5. 转换 m4a 到 mp3 (使用新的 FFmpeg CLI 函数)
            if audio_download_success:
                m4a_filepath = os.path.join(output_folder, m4a_filename)
                mp3_filename = f"{video_title}_audio.mp3"
                mp3_filepath = os.path.join(output_folder, mp3_filename)

                conversion_success = convert_m4a_to_mp3_ffmpeg_cli(m4a_filepath, mp3_filepath, bitrate="192k") # 可以调整比特率，例如 "320k"

                if conversion_success:
                    # 6. 询问用户是否要重命名MP3文件
                    mp3_filepath = rename_mp3_file(mp3_filepath, video_title)
                    
                    # 7. 询问用户是否要添加元数据
                    # 使用最终的文件名作为标题（去除扩展名）
                    final_title = os.path.splitext(os.path.basename(mp3_filepath))[0]
                    metadata_info = get_user_metadata(final_title)
                    if metadata_info is not None:
                        cover_filepath = os.path.join(output_folder, cover_filename)
                        add_metadata_to_mp3(
                            mp3_filepath, 
                            cover_filepath, 
                            final_title,
                            artist=metadata_info.get('artist', ''),
                            album=metadata_info.get('album', ''),
                            year=metadata_info.get('year', '')
                        )
                    
                    # 8. 询问是否删除原始的 .m4a 文件
                    delete_m4a = input("是否删除原始的 .m4a 文件？(y/n): ").lower().strip()
                    if delete_m4a == 'y':
                        try:
                            os.remove(m4a_filepath)
                            print(f"已删除原始文件: {m4a_filepath}")
                        except OSError as e:
                            print(f"删除文件失败: {e}")
            else:
                print("[音频转换] 跳过转换，因为 .m4a 文件下载失败。")

        except requests.exceptions.RequestException as e:
            print(f"网络请求失败: {e}")
        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            print("\n------------------------------------\n")

if __name__ == "__main__":
    main()