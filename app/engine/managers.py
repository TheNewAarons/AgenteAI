import os
import json
from config import BASE_DIR, VECTOR_DB_DIR
from app.engine.vectordb import VectorDB

class ContextManager:
    """Manages RAG context via Vector DB."""
    def __init__(self, context_dir: str):
        self.context_dir = context_dir
        self.db_path = VECTOR_DB_DIR
        self.vdb = VectorDB(self.db_path)
        self._index_context()

    def _index_context(self):
        """Updates vector database if documents changed."""
        if not os.path.isdir(self.context_dir):
            return

        docs = []
        ids = []
        metadatas = []
        
        for filename in os.listdir(self.context_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(self.context_dir, filename)
                try:
                    mtime = os.path.getmtime(filepath)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    if content:
                        docs.append(content)
                        ids.append(filename)
                        metadatas.append({"source": filename, "mtime": mtime})
                except Exception as e:
                    print(f"Indexing error {filename}: {e}")
        
        if docs:
            self.vdb.add_documents(docs, ids, metadatas)

    def load_all(self) -> str:
        """Loads all context files."""
        context_blocks = []
        if os.path.isdir(self.context_dir):
            for filename in sorted(os.listdir(self.context_dir)):
                if filename.endswith(".md"):
                    filepath = os.path.join(self.context_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        context_blocks.append(f"### {filename}\n{f.read()}")
        return "\n\n".join(context_blocks)

    def search(self, query: str) -> str:
        """Retrieves relevant fragments via RAG."""
        return self.vdb.query(query, n_results=3)

class HistoryManager:
    """Manages chat history persistence."""
    def __init__(self, history_file: str):
        self.history_file = history_file

    def load(self) -> list:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"History load error: {e}")
        return []

    def save(self, chat_session):
        try:
            history_entries = []
            for message in chat_session.history:
                parts = []
                for part in message.parts:
                    if hasattr(part, 'text') and part.text:
                        parts.append({"text": part.text})
                    elif hasattr(part, 'function_call') and part.function_call:
                        parts.append({
                            "function_call": {
                                "name": part.function_call.name,
                                "args": dict(part.function_call.args)
                            }
                        })
                    elif hasattr(part, 'function_response') and part.function_response:
                        parts.append({
                            "function_response": {
                                "name": part.function_response.name,
                                "response": dict(part.function_response.response)
                            }
                        })
                history_entries.append({
                    "role": message.role,
                    "parts": parts
                })
            
            os.makedirs(os.path.dirname(os.path.abspath(self.history_file)), exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history_entries, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"History save error: {e}")

    def clear(self):
        if os.path.exists(self.history_file):
            os.remove(self.history_file)

class TaskManager:
    """Manages complex objective sub-tasks."""
    def __init__(self, tasks_file: str):
        self.tasks_file = tasks_file

    def load(self) -> list:
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return []

    def save(self, tasks: list):
        os.makedirs(os.path.dirname(os.path.abspath(self.tasks_file)), exist_ok=True)
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)

    def add_tasks(self, task_descriptions: list):
        tasks = []
        for i, desc in enumerate(task_descriptions):
            tasks.append({
                "id": i + 1,
                "description": desc,
                "status": "Pendiente",
                "result": ""
            })
        self.save(tasks)
        return tasks

    def update_task(self, task_id: int, status: str, result: str = ""):
        tasks = self.load()
        for t in tasks:
            if t["id"] == task_id:
                t["status"] = status
                if result:
                    t["result"] = result
                break
        self.save(tasks)
        return tasks
