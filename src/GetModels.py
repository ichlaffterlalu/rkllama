import os

MODEL_PATH = "~/RKLLAMA/models"

def GetModels():
    print("Retrieving models...")

    if not os.path.exists(MODEL_PATH):
        print("The models folder did not exist.\nCreating it...")
        os.mkdir(MODEL_PATH)

    models_list = []

    for root, dirs, files in os.walk(MODEL_PATH):
        for file in files:
            if file.endswith(".rkllm"):
                models_list.append(file)

    print("Number of valid models:", len(models_list), "\n")

    return models_list
