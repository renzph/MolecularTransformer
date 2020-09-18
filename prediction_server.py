import json
import socketserver

from prediction_wrapper import TransformerReactionModel


class MolecularTransformerHandler(socketserver.StreamRequestHandler):
    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        self.data = self.rfile.readline().strip()
        reactants = json.loads(self.data.decode('utf-8'))

        products, scores = reaction_model.predict_reaction_batch(reactants)

        result = json.dumps([products, scores]).encode('utf-8')
        self.wfile.write(result)


if __name__ == "__main__":
    # TODO: Add command line arguments

    HOST, PORT = "localhost", 9999
    reaction_model = TransformerReactionModel()

    # Create the server, binding to localhost on port 9999
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((HOST, PORT), MolecularTransformerHandler)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
