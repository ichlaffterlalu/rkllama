import ctypes, sys
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
        Note: The data must be retrieved during the current callback; if not obtained in time, the pointer will be released during the next callback.
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
        # Monitor if the current byte data is complete; if incomplete, save it for later analysis
        try:
            global_text.append((split_byte_data + result.contents.text).decode('utf-8'))
            print((split_byte_data + result.contents.text).decode('utf-8'), end='')
            split_byte_data = bytes(b"")
        except:
            split_byte_data += result.contents.text
        sys.stdout.flush()
