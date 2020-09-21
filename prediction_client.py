import argparse
import json
import socket


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
            sock.connect((self.host, self.port))

            # sock.sendall(bytes(data + "\n", "utf-8"))
            sock.sendall(reactants)

            # Receive data from the server and shut down
            products, scores = json.loads(str(sock.recv(1024), "utf-8"))

        return products, scores


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Get reaction prediction results from a remote server')
    parser.add_argument('--host', default='localhost', help='Host address')
    parser.add_argument('--port', default=9999, help='Port to use')
    parser.add_argument('-o', default=None, help='Output file')
    parser.add_argument('-i', default='dummy_reactants.txt', help='Reactant input')
    args = parser.parse_args()

    with open(args.i) as f:
        reactants = f.read().split()

    reaction_model = MolecularTransformerClient(args.host, args.port)
    products, scores = reaction_model.predict_product(reactants)

    if args.o is not None:
        outfile = open(args.o, 'w')
    else:
        outfile = None

    for p, s in zip(products, scores):
        print("{}, {}".format(p, s), file=outfile)

    if outfile:
        outfile.close()
