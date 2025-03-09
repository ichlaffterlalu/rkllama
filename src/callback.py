import ctypes, sys
import time
from .classes import *
from .variables import *

# Define the callback function
def callback_impl(result, user_data, state):
    global split_byte_data

    if state == LLMCallState.RKLLM_RUN_FINISH:
        global_status = state
        print("\n")
        sys.stdout.flush()
    elif state == LLMCallState.RKLLM_RUN_ERROR:
        global_status = state
        print("execution error")
        sys.stdout.flush()
    elif state == LLMCallState.RKLLM_RUN_GET_LAST_HIDDEN_LAYER:
        '''
        If you use the GET_LAST_HIDDEN_LAYER function, the callback interface will return the memory pointer: last_hidden_layer,
        the number of tokens: num_tokens, and the size of the hidden layer: embd_size.
        With these three parameters, you can retrieve the data from last_hidden_layer.
        Note: The data must be retrieved during the current callback; if not obtained in time, the pointer will be freed during the next callback.
        '''
        if result.last_hidden_layer.embd_size != 0 and result.last_hidden_layer.num_tokens != 0:
            data_size = result.last_hidden_layer.embd_size * result.last_hidden_layer.num_tokens * ctypes.sizeof(ctypes.c_float)
            print(f"data_size: {data_size}")

            global_text.append(f"data_size: {data_size}\n")
            output_path = os.getcwd() + "/last_hidden_layer.bin"

            with open(output_path, "wb") as output_file:
                data = ctypes.cast(result.last_hidden_layer.hidden_states, ctypes.POINTER(ctypes.c_float))
                float_array_type = ctypes.c_float * (data_size // ctypes.sizeof(ctypes.c_float))
                float_array = float_array_type.from_address(ctypes.addressof(data.contents))
                output_file.write(bytearray(float_array))
                print(f"Data saved in {output_path} successfully!")
                global_text.append(f"Data saved in {output_path} successfully!")
        else:
            print("Invalid hidden layer data.")
            global_text.append("Invalid hidden layer data.")

        global_status = state
        time.sleep(0.05)  # Wait for 0.05 seconds to wait for the output result
        sys.stdout.flush()
    else:
        # Save the output token text and the execution state of RKLLM
        global_status = state
        # Check if result or result.contents or result.contents.text is None
        try:
            # Add defensive checks to prevent None concatenation
            if result and result.contents and result.contents.text:
                text_bytes = result.contents.text
                if not isinstance(text_bytes, bytes):
                    # If not bytes, try to convert or use empty bytes
                    try:
                        text_bytes = bytes(text_bytes)
                    except:
                        text_bytes = b""

                # Now safely concatenate
                try:
                    decoded_text = (split_byte_data + text_bytes).decode('utf-8')
                    global_text.append(decoded_text)
                    print(decoded_text, end='')
                    split_byte_data = bytes(b"")
                except UnicodeDecodeError:
                    # Handle incomplete UTF-8 sequences
                    split_byte_data += text_bytes
            else:
                # Handle case where text is None
                if split_byte_data:
                    try:
                        # Try to decode any accumulated bytes
                        decoded_text = split_byte_data.decode('utf-8')
                        global_text.append(decoded_text)
                        print(decoded_text, end='')
                        split_byte_data = bytes(b"")
                    except UnicodeDecodeError:
                        # Still incomplete, keep for next time
                        pass
        except Exception as e:
            print(f"\nError processing callback: {str(e)}", end='')

        sys.stdout.flush()
