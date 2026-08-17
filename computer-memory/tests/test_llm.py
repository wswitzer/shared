from computer_memory.llm import OpenAICompatibleClient


class FakeTransport:
    def __init__(self):
        self.request = None

    def post_json(self, url, payload, timeout):
        self.request = (url, payload, timeout)
        return {"choices": [{"message": {"content": "# Morning handoff\nContinue the tests."}}]}


def test_openai_compatible_client_works_with_local_endpoint():
    transport = FakeTransport()
    client = OpenAICompatibleClient(base_url="http://localhost:11434/v1", model="qwen3:14b", transport=transport)
    text = client.summarize("evidence json")
    assert text.startswith("# Morning handoff")
    assert transport.request[0] == "http://localhost:11434/v1/chat/completions"
    assert transport.request[1]["model"] == "qwen3:14b"
    assert "Do not invent" in transport.request[1]["messages"][0]["content"]
