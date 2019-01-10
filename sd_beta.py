# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 23:04:49 2018

@author: MZAIDGAUR
"""

import sys
sys.path.append("../M2_Speech_Signal_Processing")
import os.path
import cntk
import numpy as np
import scipy.sparse
import scipy.misc
import re
import time
import itertools
from collections import namedtuple
import argparse
import speech_recognition as sr
from htk_featio import read_htk_user_feat
from typing import List
import operator

def feature_stacker(x, context_frames=11):
    return np.column_stack([
        x[np.minimum(len(x) - 1, np.maximum(0, np.arange(len(x), dtype=np.int) + d))]
        for d in range(-context_frames, context_frames + 1)
    ])


def parse_script_line(script_line: str, script_path: str):
    m = re.match(r'(.*)\.feat=(.*)\[(\d+),(\d+)\]', script_line)
    assert(m)
    utt = m.group(1)
    arc = m.group(2)
    frame_start = int(m.group(3))
    frame_end = int(m.group(4))
    m = re.match(r'\.\.\.[/\\](.*)', arc)
    if m:
        arc = os.path.join(script_path, m.group(1))
    return utt, arc, frame_start, frame_end

def load_parameters(script_line: str, script_path: str):
    utt, arc, frame_start, frame_end = parse_script_line(script_line, script_path)
    feat = read_htk_user_feat(arc)
    assert( frame_start == 0 )
    assert( frame_end + 1 - frame_start == len(feat))
    return feat, utt


def decode(line,trn_file,b_width,l_weight,z,fst,mode):
     script_path = ""
     time_start = time.time()
     frames_processed = 0
     try:
          if mode==0:
               with open(trn_file, 'w', buffering=1) as ftrn:
                    feats, utterance_name = load_parameters(line.rstrip(), script_path)
                    feats = feature_stacker(feats)
                    activations = z.eval(feats.astype('f'))[0]
                    hypothesis = fst.decode(activations, beam_width=b_width, lmweight=l_weight)
                    words = [
                         x for x in
                         map(operator.itemgetter(1), hypothesis)
                         if x not in ("<eps>", "<s>", "</s>")
                         ]
                    #words.append('({})\n'.format(utterance_name))
                    ftrn.write(' '.join(words))
                    print(' '.join(words))
                    return ' '.join(words)
                    frames_processed += len(feats)
          elif(mode==1):
               r = sr.Recognizer()
               with sr.AudioFile('rec.wav') as source:
                    audio = r.record(source)
               text="Sorry, Could not recognize"
               try:
                    text = r.recognize_google(audio)
               except:
                    pass
               with open(trn_file, 'w', buffering=1) as ftrn:
                    ftrn.write(text)
                    print(text)
                    return text
     except KeyboardInterrupt:
          print("[CTRL+C detected]")
     time_end = time.time()
     #print('{:.1f} seconds, {:.2f} frames per second'.format(time_end-time_start, frames_processed / (time_end-time_start)))


def main(am,d_graph,label_map):
    z = load_model(am)
    fst = FST(d_graph, label_map)
    return z,fst

def load_model(model_filename:str):
    cntk_model = cntk.load_model(model_filename)


    model_output = cntk_model.find_by_name('ScaledLogLikelihood')



    if model_output is None:
        model_output = cntk_model.outputs[0]


    cntk_model = cntk.combine(model_output)



    if 0 == cntk.use_default_device().type():
        cntk_model = cntk.misc.convert_optimized_rnnstack(cntk_model)

    return cntk_model


Token = namedtuple('token', 'id prev_id arc_number am_score lm_score')
Arc = namedtuple('arc', 'index source_state target_state ilabel olabel cost')

class token_manager:

    def __init__(self):


        self.tokens = []


        self.active_tokens = [Token(id=0, prev_id=-1, arc_number=0, am_score=0, lm_score=0)]


        self.last_token_id = self.active_tokens[0].id


    def advance_token(self, prev_token: Token, next_arc, am_score, lm_score):
        self.last_token_id += 1
        return Token(
            self.last_token_id,
            prev_token.id,
            next_arc,
            prev_token.am_score + am_score,
            prev_token.lm_score + lm_score
        )

    def flatten_active_token_list(self, num_arcs: int, tok_list: List[Token]):

        v = np.array([x.am_score + x.lm_score for x in tok_list], dtype=np.float32)
        v = np.exp(v - np.max(v))

        r = np.array([x.arc_number for x in tok_list], dtype=np.int)
        c = np.zeros(r.shape)
        score = scipy.sparse.csc_matrix(
            (v, (r, c)),
            shape=(num_arcs,1),
            dtype=np.float32
        )

        token_index = np.ones(num_arcs, dtype=np.int32)*-1
        for i, x in enumerate(tok_list):
            token_index[x.arc_number] = i

        return score, token_index

    def tok_backtrace(self, looking_for_tokid=None):

        if looking_for_tokid is None:
            looking_for_tokid = max(self.active_tokens, key=lambda x: x.am_score + x.lm_score).id

        path=[]
        for tok in (self.tokens + self.active_tokens)[::-1]:
            if tok.id == looking_for_tokid:
                arc_number = tok.arc_number
                path.append(arc_number)
                looking_for_tokid = tok.prev_id
        path = path[::-1]


        segments = [k for k, x in itertools.groupby(path)]

        return segments

    def commit_active_tokens(self):
        self.tokens += self.active_tokens

    def beam_prune(self, beam_width: int):
        if len(self.active_tokens) > beam_width:
            self.active_tokens = sorted(
                self.active_tokens, key=lambda x: x.am_score + x.lm_score, reverse=True
            )[0:beam_width]


class FST:
    def __init__(self, fst_file: str, label_mapping: str=None):
        self._arcs = []
        self._final = {}
        self._index2label = []
        self._label2index = {}

        self._load_map(label_mapping)
        self._load_fst(fst_file)

    def _preprocess_activations(self, act):
        return (act - np.max(act, axis=1).reshape((act.shape[0], 1)))


    def decode(self, act, beam_width, lmweight, alignment: List[str]=None, ftrans=None, etrans=None, strans=None):

        if alignment is not None:
            alignment = [self._label2index[x] for x in alignment]


        if ftrans is None:
            ftrans = self.emit_trans
        if etrans is None:
            etrans = self.eps_trans
        if strans is None:
            strans = self.log_score


        act = self._preprocess_activations(act) / lmweight


        tm = token_manager()

        def do_forward(tok_list, transition_matrix, obs_vector=None):
            src_score, src_token_index = tm.flatten_active_token_list(len(self._arcs), tok_list)

            trans = transition_matrix.multiply(src_score.T)

            row_to_column = np.array(trans.argmax(axis=1)).squeeze()
            active_rows = trans.max(axis=1).nonzero()[0]


            new_tok = [
                tm.advance_token(
                    tok_list[src_token_index[row_to_column[r]]],
                    r,
                    obs_vector[self._arcs[r].ilabel] if obs_vector is not None else 0,
                    strans[r, row_to_column[r]]
                )
                for r in active_rows
            ]
            return new_tok


        for t, obs in enumerate(act):

            tm.commit_active_tokens()


            tm.active_tokens = do_forward(tm.active_tokens, ftrans, np.array(obs).squeeze())


            tm.beam_prune(beam_width)


            epsilon_tokens = []
            prev_tokens = tm.active_tokens
            while len(prev_tokens)>0:
                prev_tokens = do_forward(prev_tokens, etrans)
                epsilon_tokens += prev_tokens


            epsilon_tokens = [
                max(x, key=lambda token: token.am_score + token.lm_score)
                for k, x in itertools.groupby(
                    sorted(
                        epsilon_tokens,
                        key=lambda token: token.arc_number
                    ),
                    key=lambda token: token.arc_number)
            ]


            epsilon_tokens.sort(key=lambda token: token.id)

            tm.active_tokens += epsilon_tokens

        tm.commit_active_tokens()
        dest_state = [self._arcs[x.arc_number].target_state for x in tm.active_tokens]
        tm.active_tokens = [
            Token(x.id, x.prev_id, x.arc_number, x.am_score, x.lm_score - self._final[s])
            for x, s in zip(tm.active_tokens, dest_state) if s in self._final
        ]

        best_tok = max(tm.active_tokens, key=lambda x: x.am_score + x.lm_score)
        #print(
         #   "best cost: AM={} LM={} JOINT={}".format(
          #      best_tok.am_score, best_tok.lm_score, best_tok.am_score + best_tok.lm_score
           # )
        #)


        return  map(lambda arc: (self._index2label[arc.ilabel], arc.olabel),
            map(lambda arc_number: self._arcs[arc_number],
                tm.tok_backtrace()
            )
        )

    def _load_map(self, filename):
        with open(filename) as f:
            self._index2label = [
                '[' + x.rstrip().replace('.', '_') + ']' for x in f
            ]
        self._label2index = {'<s>': -1, '<eps>': -2}
        for i, x in enumerate(self._index2label):
            self._label2index[x] = i
        self._index2label += ['<eps>', '<s>']

    def _load_fst(self, filename):
        arcout = []
        self._final = {}
        self._arcs = []


        self._arcs.append(Arc(0, -1, 0, self._label2index['<eps>'], '<eps>', float(0)))


        def process_final_state(parts):
            assert (len(parts) in (1, 2))
            self._final[int(parts[0])] = float(parts[1] if len(parts) > 1 else 0)
        def process_normal_arc(parts):
            assert (len(parts) in (4, 5))

            sorc = int(parts[0])
            dest = int(parts[1])
            ilab = self._label2index[parts[2]]
            olab = parts[3]
            cost = float(parts[4] if len(parts) > 4 else 0)

            self._arcs.append(Arc(len(self._arcs), sorc, dest, ilab, olab, cost))
        with open(filename) as f:
            for line in f:
                parts = line.rstrip().split()
                if len(parts) <= 2:
                    process_final_state(parts)
                else:
                    process_normal_arc(parts)


        arcout = [() for _ in range(1 + max(x.source_state for x in self._arcs))]
        for source_state, arcs in itertools.groupby(
                sorted(self._arcs, key=lambda arc: arc.source_state),
                key= lambda arc: arc.source_state):
            arcout[source_state] = [arc.index for arc in arcs]



        emit_row, emit_col, emit_val = [], [], []
        eps_row, eps_col, eps_val = [], [], []

        for arc in self._arcs:
            if arc.ilabel >= 0:
                emit_col.append(arc.index)
                emit_row.append(arc.index)
                emit_val.append(float(0))
            next_state = arc.target_state
            for next_arc_index in arcout[next_state]:
                next_arc = self._arcs[next_arc_index]
                score = -next_arc[-1]
                if next_arc.ilabel >= 0:

                    emit_col.append(arc.index)
                    emit_row.append(next_arc_index)
                    emit_val.append(score)
                else:

                    eps_col.append(arc.index)
                    eps_row.append(next_arc_index)
                    eps_val.append(score)


        self.emit_trans = scipy.sparse.csr_matrix(
            (np.exp(emit_val), (emit_row, emit_col)),
            shape=(len(self._arcs), len(self._arcs)),
            dtype=np.float32
        )
        self.eps_trans = scipy.sparse.csr_matrix(
            (np.exp(eps_val), (eps_row, eps_col)),
            shape=(len(self._arcs), len(self._arcs)),
            dtype=np.float32
        )
        self.log_score = scipy.sparse.csr_matrix(
            (emit_val + eps_val, (emit_row + eps_row, emit_col + eps_col)),
            shape=(len(self._arcs), len(self._arcs)),
            dtype=np.float32
        )

