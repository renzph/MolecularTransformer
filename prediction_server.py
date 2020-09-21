import argparse
import json
import socketserver

from prediction_wrapper import TransformerReactionModel


class MolecularTransformerHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.data = self.rfile.readline().strip()
        reactants = json.loads(self.data.decode('utf-8'))

        products, scores = reaction_model.predict_reaction_batch(reactants)
        result = json.dumps([products, scores]).encode('utf-8')
        self.wfile.write(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Serve MolecularTransformer reaction prediction.')
    parser.add_argument('--host', default='localhost', help='Host address')
    parser.add_argument('--port', default=9999, help='Port to use')

    args = parser.parse_args()

    reaction_model = TransformerReactionModel()

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((args.host, args.port), MolecularTransformerHandler)

    server.serve_forever()
