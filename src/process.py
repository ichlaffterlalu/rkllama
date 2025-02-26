import threading, time, json
from transformers import AutoTokenizer
from flask import Flask, request, jsonify, Response
import src.variables as variables


def Request(model_rkllm):

    try:
        # Put the server in a locked state.
        isLocked = True

        data = request.json
        if data and 'messages' in data:
            # Reset global variables.
            variables.global_status = -1

            # Define the structure of the returned response.
            llmResponse = {
                "id": "rkllm_chat",
                "object": "rkllm_chat",
                "created": None,
                "choices": [],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "tokens_per_second": 0,
                    "total_tokens": 0
                }
            }

            # Retrieve chat history from the JSON request
            messages = data["messages"]

            # Set up the tokenizer
            tokenizer = AutoTokenizer.from_pretrained(variables.model_id, trust_remote_code=True)
            supports_system_role = "raise_exception('System role not supported')" not in tokenizer.chat_template

            if variables.system and supports_system_role:
                prompt = [{"role": "system", "content": variables.system}] + messages
            else:
                prompt = messages

            for i in range(1, len(prompt)):
                if prompt[i]["role"] == prompt[i - 1]["role"]:
                    raise ValueError("Roles must alternate between 'user' and 'assistant'.")

            # Set up the chat template
            prompt = tokenizer.apply_chat_template(prompt, tokenize=True, add_generation_prompt=True)
            llmResponse["usage"]["prompt_tokens"] = llmResponse["usage"]["total_tokens"] = len(prompt)

            output_rkllm = ""

            if not "stream" in data.keys() or data["stream"] == False:
                # Create a thread for model inference.
                thread_model = threading.Thread(target=model_rkllm.run, args=(prompt,))
                try:
                    thread_model.start()
                    print("Inference thread started")
                except Exception as e:
                    print("Error starting the thread:", e)

                # Wait for the model to finish and periodically check the inference thread.
                threadFinish = False
                count = 0
                start = time.time()

                while not threadFinish:
                    while len(variables.global_text) > 0:
                        count += 1
                        output_rkllm += variables.global_text.pop(0)
                        time.sleep(0.005)

                        thread_model.join(timeout=0.005)
                    threadFinish = not thread_model.is_alive()

                total = time.time() - start
                llmResponse["choices"] = [{
                    "role": "assistant",
                    "content": output_rkllm,
                    "logprobs": None,
                    "finish_reason": "stop"
                }]
                llmResponse["usage"]["total_tokens"] = count + llmResponse["usage"]["prompt_tokens"]
                llmResponse["usage"]["completion_tokens"] = count
                llmResponse["usage"]["tokens_per_second"] = count / total
                return jsonify(llmResponse), 200

            else:
                def generate():
                    thread_model = threading.Thread(target=model_rkllm.run, args=(prompt,))
                    thread_model.start()

                    thread_model_finished = False
                    count = 0
                    start = time.time()

                    while not thread_model_finished:
                        while len(variables.global_text) > 0:
                            count += 1
                            output_rkllm = variables.global_text.pop(0)

                            llmResponse["choices"] = [
                                {
                                "role": "assistant",
                                "content": output_rkllm,
                                "logprobs": None,
                                "finish_reason": "stop" if variables.global_status == 1 else None,
                                }
                            ]
                            llmResponse["usage"]["completion_tokens"] = count
                            llmResponse["usage"]["total_tokens"] += 1
                            yield f"{json.dumps(llmResponse)}\n\n"

                        # Calculate processing time
                        total = time.time() - start

                        # Calculate tokens per second and total tokens
                        llmResponse["usage"]["tokens_per_second"] = count / total

                        thread_model.join(timeout=0.005)
                        thread_model_finished = not thread_model.is_alive()

                return Response(generate(), content_type='text/plain')
        else:
            return jsonify({'status': 'error', 'message': 'Invalid JSON data!'}), 400
    finally:
        variables.lock.release()
        isLocked = False
