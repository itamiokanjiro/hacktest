import gradio as gr
from modules import script_callbacks

def connect(ip, port, connected):
    if connected:
        return f"❌ 已斷開 {ip}:{port}", False, "建立遠程連接"
    else:
        return f"✅ 已連接到 {ip}:{port}", True, "斷開連接"

def on_ui_tabs():
    with gr.Blocks() as demo:
        gr.Markdown("## 🌐 遠程連接擴展 (範例UI)")

        with gr.Row():
            ip = gr.Textbox(label="IP地址", value="192.168.1.104")
            port = gr.Textbox(label="端口", value="7887")

        status = gr.Textbox(label="狀態", value="未連接")
        btn = gr.Button("建立遠程連接")
        connected_state = gr.State(False)

        btn.click(
            fn=connect,
            inputs=[ip, port, connected_state],
            outputs=[status, connected_state, btn]
        )

    return [(demo, "遠程連接", "remote_connect_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)
