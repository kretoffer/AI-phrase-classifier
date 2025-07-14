from config import k

def auto_select_epochs(dataset_len, learning_rate, k: int = k):
    epochs = int(k/(dataset_len*learning_rate))
    return epochs