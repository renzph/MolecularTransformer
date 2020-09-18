import json
import socket

HOST, PORT = "localhost", 9999

class MolecularTransformerClient():
    """Connect to a server running the molecular transformer"""
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def predict_product(self, reactants):
        """Predicts the products for  a batch of reactions

        Args:
            reactants: List of SMILES where reactants are separated by dots

        Returns:
            products: A list of products
            uncertainty???
        """

        reactants = (json.dumps(reactants) + '\n').encode('utf-8')

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((HOST, PORT))

            # sock.sendall(bytes(data + "\n", "utf-8"))
            sock.sendall(reactants)

            # Receive data from the server and shut down
            products, scores = json.loads(str(sock.recv(1024), "utf-8"))

        return products, scores

if __name__ == "__main__":
    with open('dummy_reactants.json') as f:
        dummy_reactants = json.load(f)


    reaction_model = MolecularTransformerClient(HOST, PORT)
    products, scores = reaction_model.predict_product(dummy_reactants)

    print(products, scores)
