import os
import streamlit as st
import subprocess
import threading
import queue
import time

# ========== Config (adjust your API key and model below) ==========
OPENAI_KEY = os.environ['OPENAI_API_KEY']  # <-- replace with your OpenAI key
AIDER_COMMAND = f"aider --model o3-mini --api-key openai={OPENAI_KEY} --no-auto-commits"

# ========== Background Thread: Reads output from aider ==========
def read_output(process, complete_log_queue, partial_log_queue, stop_event, complete_logs, partial_logs):
    partial_line = ""
    while not stop_event.is_set():
        char = process.stdout.read(1)  # Read one character at a time
        if char:
            partial_line += char
            if char == "\n":  # If a newline character is encountered
                complete_log_queue.put(partial_line.rstrip())  # Send the complete line
                partial_line = ""  # Reset the partial line
                # Clear the partial log queue
                while not partial_log_queue.empty():
                    partial_log_queue.get()
                    
                partial_logs.clear()
                
            else:
               # Clear the partial log queue and update it with the current partial line
                while not partial_log_queue.empty():
                    partial_log_queue.get()
                partial_log_queue.put(partial_line.rstrip())
                
        elif process.poll() is not None:  # If the process has ended
            break

    # Ensure any remaining partial line is sent before exiting
    if partial_line:
        complete_log_queue.put(partial_line.rstrip())
        partial_log_queue.put(partial_line.rstrip())

    stop_event.set()
    complete_log_queue.put("🔚 Aider session ended.")
    partial_log_queue.put("🔚 Aider session ended.")
# ========== Start the aider subprocess ==========
def start_aider():
    return subprocess.Popen(
        AIDER_COMMAND,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True,
        bufsize=1
    )

# ========== Streamlit App ==========
st.title("💬 Aider Interactive Terminal (Chat-Like)")

# -- Initialize session state --
if "process" not in st.session_state:
    st.session_state.process = None
if "complete_log_queue" not in st.session_state:
    st.session_state.complete_log_queue = queue.Queue()
if "partial_log_queue" not in st.session_state:
    st.session_state.partial_log_queue = queue.Queue()
if "complete_logs" not in st.session_state:
    st.session_state.complete_logs = []
if "partial_logs" not in st.session_state:
    st.session_state.partial_logs = []
if "reader_thread" not in st.session_state:
    st.session_state.reader_thread = None
if "stop_event" not in st.session_state:
    st.session_state.stop_event = threading.Event()
if "aider_running" not in st.session_state:
    st.session_state.aider_running = False

# -- Start Aider --
if st.button("🚀 aider-install / Start Session", disabled=st.session_state.aider_running):
    try:
        st.session_state.process = start_aider()
        st.session_state.stop_event.clear()
        st.session_state.aider_running = True

        st.session_state.reader_thread = threading.Thread(
            target=read_output,
            args=(
                st.session_state.process,
                st.session_state.complete_log_queue,
                st.session_state.partial_log_queue,
                st.session_state.stop_event,
                st.session_state.complete_logs,
                st.session_state.partial_logs
            ),
            daemon=True
        )
        st.session_state.reader_thread.start()
        st.success("✅ Aider session started.")
    except Exception as e:
        st.error(f"❌ Failed to start Aider: {e}")

# -- Display output logs --
# while not st.session_state.log_queue.empty():
#     st.session_state.logs.append(st.session_state.log_queue.get())
# -- Update logs from the queues --
def update_logs(complete_log_queue, complete_logs, partial_log_queue, partial_logs):
    while not complete_log_queue.empty():
        complete_logs.append(complete_log_queue.get())
    while not partial_log_queue.empty():
        partial_logs.append(partial_log_queue.get())

update_logs(
    st.session_state.complete_log_queue,
    st.session_state.complete_logs,
    st.session_state.partial_log_queue,
    st.session_state.partial_logs
)
# -- Display logs --
st.subheader("🖥️ Complete Lines")
st.text_area(
    "Complete Logs",
    "\n".join(st.session_state.complete_logs[-100:]),
    height=200,
    key="complete_log_area",
    disabled=True
)

st.subheader("🖥️ Partial Lines")
st.text_area(
    "Partial Logs",
    "\n".join(st.session_state.partial_logs[-100:]),
    key="partial_log_area",
    disabled=True
)
# Input and controls
if st.session_state.aider_running:
    user_input = st.text_input("📝 Your Prompt:", key="user_prompt")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📤 Send", use_container_width=True):
            if user_input.strip():
                try:
                    st.session_state.process.stdin.write(user_input + "\n")
                    st.session_state.process.stdin.flush()

                      # Clear the partial log queue
                    while not st.session_state.partial_log_queue.empty():
                        st.session_state.partial_log_queue.get()

                    # Clear the partial logs display
                    st.session_state.partial_logs.clear()

                    st.success("Prompt sent to Aider.")
                    st.rerun()  # to clear input
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Type something to send.")
    with col2:
        if st.button("🔄 Refresh Logs", use_container_width=True):
            update_logs(
                st.session_state.complete_log_queue,
                st.session_state.complete_logs,
                st.session_state.partial_log_queue,
                st.session_state.partial_logs
            )
            st.rerun()
    with col3:
        if st.button("🛑 Stop Session", use_container_width=True):
            st.session_state.stop_event.set()
            st.session_state.process.terminate()
            st.session_state.process = None
            st.session_state.aider_running = False
            st.success("🛑 Aider session stopped.")

# -- Instructional flow for your case --
with st.expander("📋 Sample Flow Steps (for testing)"):
    st.markdown("""
    1. Click **Start Session** (starts aider with your API key).
    2. Paste prompts like:

       - `write a FAST API python code to perform CRUD to manage Candidate Details in Postgres DB. pls follow mvc pattern`
       - `conv continue` (continue the conversation multiple times)
    3. Use **Stop Session** to manually terminate (`Ctrl+C` equivalent).
    """)

