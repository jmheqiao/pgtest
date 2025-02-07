async def main():
    print("开始获取频道最新消息...")

    # 创建更新文件目录
    if not os.path.exists(updated_files_dir):
        os.makedirs(updated_files_dir)
        print(f"更新文件目录已创建：{updated_files_dir}")
    else:
        print(f"更新文件目录已存在：{updated_files_dir}")

    # 获取频道最新消息
    async for message in client.iter_messages(channel_username, limit=1):
        if message.media:
            attachment_name = message.file.name
            print(f"获取到最新消息的附件名称：{attachment_name}")

            # 对比当前目录内的zip文件名称
            zip_files = [f for f in os.listdir(current_dir) if f.endswith('.zip')]
            if attachment_name in zip_files:
                print("附件名称与当前目录内的zip文件名称一致，无需更新，脚本退出。")
                return

            print("附件名称与当前目录内的zip文件名称不一致，开始下载...")
            await message.download_media(file=os.path.join(current_dir, attachment_name))
            print(f"附件下载完成，保存路径：{os.path.join(current_dir, attachment_name)}")

            # 如果./pgdown目录不存在，则创建
            if not os.path.exists(pgdown_dir):
                os.makedirs(pgdown_dir)
                print(f"创建了新的./pgdown目录：{pgdown_dir}")
            else:
                print(f"保留旧的./pgdown目录：{pgdown_dir}")

            # 解压到./pgdown目录内，保留文件的原始修改日期
            extract_zip_with_timestamps(os.path.join(current_dir, attachment_name), pgdown_dir)
            print(f"附件已解压到./pgdown目录内，保留了文件的原始修改日期")

            # 删除当前目录中旧的zip文件
            for old_zip in zip_files:
                if old_zip != attachment_name:
                    os.remove(os.path.join(current_dir, old_zip))
                    print(f"旧的zip文件已删除：{old_zip}")

            # 处理文件拷贝和更新逻辑
            update_files = []
            current_files = [f for f in os.listdir(updated_files_dir) if f not in [os.path.basename(__file__), attachment_name]]

            if not current_files:
                print("更新文件目录内没有其它文件，开始拷贝所有文件...")
                copy_with_timestamps(os.path.join(pgdown_dir, 'pg.jar'), updated_files_dir)
                update_files.append('pg.jar')
                for file in os.listdir(pgdown_lib_dir):
                    if not file.endswith('.md5'):
                        copy_with_timestamps(os.path.join(pgdown_lib_dir, file), updated_files_dir)
                        update_files.append(file)
            else:
                print("更新文件目录内有其它文件，开始进行对比和更新...")
                if not os.path.exists(os.path.join(updated_files_dir, 'pg.jar')) or \
                   not filecmp.cmp(os.path.join(pgdown_dir, 'pg.jar'), os.path.join(updated_files_dir, 'pg.jar')):
                    copy_with_timestamps(os.path.join(pgdown_dir, 'pg.jar'), updated_files_dir)
                    update_files.append('pg.jar')
                for file in os.listdir(pgdown_lib_dir):
                    if not file.endswith(('.md5', '.txt')):
                        if not os.path.exists(os.path.join(updated_files_dir, file)) or \
                           not filecmp.cmp(os.path.join(pgdown_lib_dir, file), os.path.join(updated_files_dir, file)):
                            copy_with_timestamps(os.path.join(pgdown_lib_dir, file), updated_files_dir)
                            update_files.append(file)

            # 转发信息到群组
            attachment_info = f"PG最新版本：{attachment_name}\n"
            update_info = f"更新的文件有：{', '.join(update_files)}\n" if update_files else "无文件更新\n"
            content_info = message.text.split('今日更新内容', 1)[1] if '今日更新内容' in message.text else "无更新内容"
            await client.send_message(group_username, attachment_info + update_info + content_info)
            print(f"更新信息已转发到群组：{group_username}")
