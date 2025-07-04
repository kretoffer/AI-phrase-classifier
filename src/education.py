import numpy as np


def educate(data, embedding_matrix, input_layer, hidden_layer, output_layer, project_path):
    weights_input_to_hidden = np.random.uniform(-0.5, 0.5, (hidden_layer, input_layer))
    weights_hidden_to_output = np.random.uniform(-0.5, 0.5, (output_layer, hidden_layer))

    bias_input_to_hidden = np.zeros((hidden_layer, 1))
    bias_hidden_to_output = np.zeros((output_layer, 1))

    epochs = 5
    e_loss = 0
    e_correct = 0
    learning_rate = 0.01

    for epoch in range(epochs):
        print(f"Epoch: {epoch+1}")

        for input_neurons, classification, tokens in data:
            input_neurons = np.reshape(input_neurons, (-1, 1))

            hidden_raw = bias_input_to_hidden + weights_input_to_hidden @ input_neurons
            hidden = 1 / (1 + np.exp(-hidden_raw)) #sigmoid

            output_raw = bias_hidden_to_output + weights_hidden_to_output @ hidden
            output = 1 / (1 + np.exp(-output_raw)) #sigmoid

            e_loss += 1 / len(output) * np.sum((output - classification) ** 2, axis=0)
            e_correct += int(np.argmax(output) == np.argmax(classification))

            #learning
            #output layer
            delta_output = output - classification
            weights_hidden_to_output += -learning_rate * delta_output @ np.transpose(hidden)
            bias_hidden_to_output += -learning_rate * delta_output

            #hidden layer
            delta_hidden = np.transpose(weights_hidden_to_output) @ delta_output * (hidden * (1 - hidden))
            weights_input_to_hidden += -learning_rate * delta_hidden @ np.transpose(input_neurons)
            bias_input_to_hidden += -learning_rate * delta_hidden

            #embedding
            grad_input = weights_input_to_hidden.T @ delta_hidden
            grad_input = grad_input.reshape(len(embedding_matrix[0]), -1)
            for i, token in enumerate(tokens):
                embedding_matrix[token] -= learning_rate * (grad_input[i] / len(tokens))


        # print(f"Loss {(e_loss / len(data)) * 100}%")
        # print(f"Correct {(e_correct / len(data)) * 100}%")
    
    np.savez(f"{project_path}/classifier.npz", 
             weights_input_to_hidden=weights_input_to_hidden,
             weights_hidden_to_output=weights_hidden_to_output,
             bias_input_to_hidden=bias_input_to_hidden,
             bias_hidden_to_output=bias_hidden_to_output,
             embedding_matrix=embedding_matrix)
