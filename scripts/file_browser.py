import os
import gradio as gr
from modules import script_callbacks

def list_files():
    """遍歷當前插件目錄並回傳檔案清單"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = []
    for root, _, filenames in os.walk(base_dir):
        for f in filenames:
            rel_path = os.path.relpath(os.path.join(root, f), base_dir)
            files.append(rel_path)
    return "\n".join(files) if files else "（無檔案）"

def on_ui_tabs():
    with gr.Blocks() as demo:
        gr.Markdown("### 📂 File Browser - 當前插件檔案清單")
        output = gr.Textbox(label="檔案清單", lines=20)
        refresh_btn = gr.Button("🔄 重新整理")

        refresh_btn.click(fn=list_files, inputs=[], outputs=[output])

        # 預設載入一次
        demo.load(fn=list_files, inputs=[], outputs=[output])

    return [(demo, "File Browser", "file_browser_tab")]

# 註冊 UI 分頁
script_callbacks.on_ui_tabs(on_ui_tabs)
