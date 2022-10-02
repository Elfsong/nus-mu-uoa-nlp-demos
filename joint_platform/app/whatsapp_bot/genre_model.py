# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2022-10-02

from . genre.hf_model import GENRE
from . genre.entity_linking import get_end_to_end_prefix_allowed_tokens_fn_hf as get_prefix_allowed_tokens_fn
from . genre.utils import get_entity_spans_hf as get_entity_spans

class GenreModel(object):
    def __init__(self):
        self.model = GENRE.from_pretrained("./app/whatsapp_bot/static/models/hf_e2e_entity_linking_aidayago").eval()

    def generate(self, sentences: list) -> list:
        prefix_allowed_tokens_fn = get_prefix_allowed_tokens_fn(self.model, sentences)
        results = self.model.sample(sentences, prefix_allowed_tokens_fn=prefix_allowed_tokens_fn)
        return results