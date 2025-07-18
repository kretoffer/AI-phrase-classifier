import numpy as np

from src.logic.neuron_activation import activate


def educate_classifier(data, embedding_matrix, input_layer, hidden_layer, output_layer, project_path, activate_method, epochs, learning_rate: float):
    weights_input_to_hidden = np.random.uniform(-0.5, 0.5, (hidden_layer, input_layer))
    weights_hidden_to_output = np.random.uniform(-0.5, 0.5, (output_layer, hidden_layer))

    bias_input_to_hidden = np.zeros((hidden_layer, 1))
    bias_hidden_to_output = np.zeros((output_layer, 1))

    e_loss = 0
    e_correct = 0

    print("Educate classifier")
    for epoch in range(epochs):
        e_loss = 0
        e_correct = 0

        for input_neurons, classification, tokens in data:
            input_neurons = np.reshape(input_neurons, (-1, 1))

            hidden_raw = bias_input_to_hidden + weights_input_to_hidden @ input_neurons
            hidden = activate(hidden_raw, activate_method)

            output_raw = bias_hidden_to_output + weights_hidden_to_output @ hidden
            output = activate(output_raw, activate_method)

            e_loss += float(1 / len(output) * np.sum((output - classification) ** 2, axis=0))
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

    print(f"Classifier was educated with {epochs} epochs")

    print(f"Loss: {round(e_loss / len(data) * 100, 3)}%")
    print(f"Accuracy: {round((e_correct / len(data)) * 100, 3)}%")
    
    np.savez(f"{project_path}/classifier.npz", 
             weights_input_to_hidden=weights_input_to_hidden,
             weights_hidden_to_output=weights_hidden_to_output,
             bias_input_to_hidden=bias_input_to_hidden,
             bias_hidden_to_output=bias_hidden_to_output,
             embedding_matrix=embedding_matrix)
    
def educate_entity_extractor(data, input_layer, hidden_layer, output_layer, project_path, activate_method, epochs, entity: str, intent: str, learning_rate: float):
    weights_input_to_hidden = np.random.uniform(-0.5, 0.5, (hidden_layer, input_layer))
    weights_hidden_to_output = np.random.uniform(-0.5, 0.5, (output_layer, hidden_layer))

    bias_input_to_hidden = np.zeros((hidden_layer, 1))
    bias_hidden_to_output = np.zeros((output_layer, 1))

    e_loss = 0
    e_correct = 0
    
    print(f"Educate {entity} extractor for {intent}")
    for epoch in range(epochs):
        e_loss = 0
        e_correct = 0

        for input_neurons, classification in data:
            input_neurons = np.reshape(input_neurons, (-1, 1))

            hidden_raw = bias_input_to_hidden + weights_input_to_hidden @ input_neurons
            hidden = activate(hidden_raw, activate_method)

            output_raw = bias_hidden_to_output + weights_hidden_to_output @ hidden
            output = activate(output_raw, activate_method)

            e_loss += float(1 / len(output) * np.sum((output - classification) ** 2, axis=0))
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

    print(f"{entity} extractor for {intent} was educated with {epochs} epohs")

    print(f"Loss: {round(e_loss / len(data) * 100, 3)}%")
    print(f"Accuracy: {round((e_correct / len(data)) * 100, 3)}%")

    np.savez(f"{project_path}/{intent}/{entity}.npz", 
             weights_input_to_hidden=weights_input_to_hidden,
             weights_hidden_to_output=weights_hidden_to_output,
             bias_input_to_hidden=bias_input_to_hidden,
             bias_hidden_to_output=bias_hidden_to_output)