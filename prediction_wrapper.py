"""This provides a wrapper around the Molecular transformer and enables
reaction prediction for a batch of reactions. This might be done in a more
efficient way but I don't want to dig into OMNT. This is adapted from translate.py"""

from __future__ import division, unicode_literals

import argparse
import os
import re
import warnings
import tempfile

import numpy as np

import onmt
import onmt.inputters
import onmt.model_builder
import onmt.modules
import onmt.opts
import onmt.translate
from onmt.translate.translator import build_translator
from onmt.utils.logging import init_logger

warnings.filterwarnings('ignore')


def smi_tokenizer(smi):
    """
    Tokenize a SMILES molecule or reaction
    """

    pattern = r"(\[[^\]]+]|Br?|Cl?|N|O|S|P|F|I|b|c|n|o|s|p|\(|\)|\.|=|#|-|\+|\\\\|\/|:|~|@|\?|>|\*|\$|\%[0-9]{2}|[0-9])"
    regex = re.compile(pattern)
    tokens = [token for token in regex.findall(smi)]
    assert smi == ''.join(tokens)
    return ' '.join(tokens)


class TransformerReactionModel():
    def __init__(
            self,
            model_path='experiments/models/MIT_mixed_augm_model_average_20.pt',
            max_length=200,
            fast=True,
            gpu=0):

        self.model_path = model_path
        self.max_length = max_length
        self.fast = fast
        self.gpu = gpu
        fast = '-fast' if fast else ''

        # create argparse and parse options from string
        dummy_parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        onmt.opts.add_md_help_argument(dummy_parser)
        onmt.opts.translate_opts(dummy_parser)

        opt = dummy_parser.parse_args(
            '-model {} -src /dev/null -replace_unk -max_length {} {} -gpu {}'.format(model_path, max_length, fast, gpu).split())

        # load the model
        self.translator = build_translator(opt, report_score=True)

    def predict_reaction_batch(self, reactants, batch_size=64):
        """Args:
            - reactants: list (n_reactions) of list of smiles (n_reactants).
        Returns:
            - products: The resulting product
            - scores: The score for the product
        """

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_src = os.path.join(tmpdirname, 'tmp_reactants')
            with open(tmp_src, 'w') as f:
                for r_dots in reactants:
                    r_list = r_dots.split('.')
                    print(' . '.join([smi_tokenizer(s)
                                      for s in r_list]), file=f)

            scores, products = self.translator.translate(
                src_path=tmp_src, batch_size=batch_size)

        # only get top prediction
        scores = [s[0].item() for s in scores]
        products = [p[0].replace(' ', '') for p in products]
        return products, scores
