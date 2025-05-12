from fastapi import FastAPI
import gradio as gr
from agent_client import run_agent
from agent_client import session_state
from fastapi import Response
import utils.agent_utils as agent_utils

api_app = FastAPI()  # 必须定义 ASGI 应用实例


# 修改 ui.py 中的 chat_respond 函数
async def chat_respond(message: str, history, request: gr.Request):
    session_id = request.session_hash
    if not session_state.has_session(session_id=session_id):
        session_id = session_state.create_session(session_id=session_id)
    print(f"Get current session from header:{request.headers}")

    try: 
        current_session = session_state.sessions[session_id]
        current_stage = current_session["stage"]
        print(f"session_id:{session_id}, current stage:{current_stage}")
        new_response = None

        # 定义每个阶段的处理函数
        async def handle_init():
            session_state.set_stage(session_id, "ask_symbol")
            return "请先输入需要分析的公司股票代码（例如：AAPL）"

        async def handle_ask_symbol():
            cleaned_symbol = message.strip().upper()
            if not agent_utils.valid(cleaned_symbol, 'symbol'):
                return f"{cleaned_symbol} 不合法，请重新输入公司股票。"
            session_state.update_param(session_id, "symbol", cleaned_symbol)
            session_state.set_stage(session_id, "ask_discount_rate")
            return f"您已输入{cleaned_symbol}, 现在输入折现率（例如：0.08 表示8%）"

        async def handle_ask_discount_rate():
            try:
                discount_rate = float(message)
                session_state.update_param(session_id, "discount_rate", discount_rate)
                session_state.set_stage(session_id, "ask_growth_rate")
                return "请输入终值增长率(0.01 - 0.03)"
            except ValueError:
                return "请输入终止增长率（例如：0.03 表示3%）"

        async def handle_ask_growth_rate():
            try:
                print("handle_ask_growth_rate")
                growth_rate = float(message)
                session_state.update_param(session_id, "growth_rate", growth_rate)
                params = session_state.sessions[session_id]["params"]
                symbol = params["symbol"]
                discount_rate = params["discount_rate"]
                growth_rate = params["growth_rate"]
                print(f"symbol:{symbol}, discount_rate:{discount_rate}, growth_rate:{growth_rate}")
                result = await run_agent(
                    symbol=params["symbol"],
                    discount_rate=params["discount_rate"],
                    growth_rate=params["growth_rate"]
                )
                session_state.set_stage(session_id, "completed")
                return result['output']
            except ValueError:
                return "终止增长率数值格式错误，请输入小数（如0.05）"

        stage_handlers = {
            "init": handle_init,
            "ask_symbol": handle_ask_symbol,
            "ask_discount_rate": handle_ask_discount_rate,
            "ask_growth_rate": handle_ask_growth_rate
        }

        new_response = await stage_handlers.get(current_stage, lambda: None)()

    except KeyError as e:
        print(f"{e}")
        new_response = f"会话出错，请重新开始。{e}"
    print(f"New response:{new_response}")
    return new_response


# 将 Gradio 挂载到 FastAPI
gradio_app = gr.ChatInterface(
    chat_respond
)
app = gr.mount_gradio_app(api_app, gradio_app, path="")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # 通过 ASGI 服务器启动
    