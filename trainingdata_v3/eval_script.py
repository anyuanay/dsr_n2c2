#!/usr/local/bin/python

"""
To run this file, please use:

python <gold standard folder> <system output folder>

e.g.: python gold_annotations system_annotations

Please note that you must use Python 3 to get the correct results with this script


"""

import argparse
from copy import deepcopy
import os
import glob
from collections import defaultdict
import statistics

index = {'Action':0, 'Negation':1, 'Temporality':2, 'Certainty':3, 'Actor':4}

class ClinicalConcept(object):
    """Named Entity Tag class."""

    def __init__(self, tid, start, end, ttype, text=''):
        """Init."""
        self.rid = str(tid).strip()
        self.start = int(start)
        self.end = int(end)
        self.text = str(text).strip()
        self.ttype = str(ttype).strip()

    def span_matches(self, other, mode='strict'):
        """Return whether the current tag overlaps with the one provided."""
        assert mode in ('strict', 'lenient')
        if mode == 'strict':
            if self.start == other.start and self.end == other.end:
                return True
        else:   # lenient
            if (self.end > other.start and self.start < other.end) or \
               (self.start < other.end and other.start < self.end):
                return True
        return False

    def equals(self, other, mode='strict'):
        """Return whether the current tag is equal to the one provided."""
        assert mode in ('strict', 'lenient')
        return other.ttype == self.ttype and self.span_matches(other, mode)

    def __str__(self):
        """String representation."""
        return '{}\t{}\t({}:{})'.format(self.ttype, self.text, self.start, self.end)

class Attribute(object):
    """Attribute class."""

    def __init__(self, rid, arg, rtype, rval):
        """Init."""
        assert isinstance(arg, ClinicalConcept)
        self.rid = str(rid).strip()
        self.arg = arg
        self.rtype = str(rtype).strip()
        self.rval = str(rval).strip()

    def equals(self, other, mode='strict'):
        """Return whether the current tag is equal to the one provided."""
        assert mode in ('strict', 'lenient')
        if self.arg.equals(other.arg, mode) and \
                self.arg.equals(other.arg, mode) and \
                self.rtype == other.rtype  and \
                self.rval == other.rval:
            return True
        return False

    def __str__(self):
        """String representation."""
        return '{} ({} dimension is {})'.format(self.arg, self.rtype,
                                    self.rval)

class RecordTrack1(object):
    """Record for Track 1 class."""

    def __init__(self, file_path):
        """Initialize."""
        self.path = os.path.abspath(file_path)
        self.basename = os.path.basename(self.path)
        self.annotations = self._get_annotations()
        # self.text = self._get_text()

    @property
    def tags(self):
        return self.annotations['tags']

    @property
    def attributes(self):
        return self.annotations['attributes']

    def _get_annotations(self):
        """Return a dictionary with all the annotations in the .ann file."""
        annotations = defaultdict(dict)
        with open(self.path) as annotation_file:
            lines = annotation_file.readlines()

            e_t_mapper=dict()
            t_e_mapper=dict()
            e_etype_mapper=dict()
            for line_num, line in enumerate(lines):
                if line.strip().startswith('E'):
                    e_id, mapper_m = line.strip().split('\t')
                    e_type, tag_id = mapper_m.split(':')
                    assert e_id not in e_t_mapper
                    assert tag_id not in t_e_mapper
                    e_t_mapper[e_id]=tag_id
                    t_e_mapper[tag_id]=e_id
                    e_etype_mapper[e_id]=e_type

            for line_num, line in enumerate(lines):
                if line.strip().startswith('T'):
                    try:
                        tag_id, tag_m, tag_text = line.strip().split('\t')
                    except ValueError:
                        print(self.path, line)
                    if len(tag_m.split(' ')) == 3:
                        tag_type, tag_start, tag_end = tag_m.split(' ')
                    elif len(tag_m.split(' ')) == 4:
                        tag_type, tag_start, _, tag_end = tag_m.split(' ')
                    elif len(tag_m.split(' ')) == 5:
                        tag_type, tag_start, _, _, tag_end = tag_m.split(' ')
                    else:
                        print(self.path)
                        print(line)
                    tag_start, tag_end = int(tag_start), int(tag_end)
                    if tag_id in t_e_mapper:
                        annotations['tags'][tag_id] = ClinicalConcept(t_e_mapper[tag_id],
                                                                    tag_start,
                                                                    tag_end,
                                                                    e_etype_mapper[t_e_mapper[tag_id]],
                                                                    tag_text)
                    annotations['tags']["D_"+tag_id] = ClinicalConcept("D_"+tag_id,
                                                                  tag_start,
                                                                  tag_end,
                                                                  'Drug',
                                                                  tag_text)

            attribute_mapper=dict()

            for line_num, line in enumerate(lines):
                if line.strip().startswith('A'):
                    attr_id, attr_m = line.strip().split('\t')
                    attr_type, attr_arg, attr_val = attr_m.split(' ')
                    arg1 = annotations['tags'][e_t_mapper[attr_arg]]
                    annotations['attributes'][attr_id] = Attribute(attr_id, arg1,
                                                                attr_type, attr_val)
                    if attr_arg not in attribute_mapper:
                        attribute_mapper[attr_arg]=['']*5
                    attribute_mapper[attr_arg][index[attr_type]] = attr_val
            for key in attribute_mapper.keys():
                annotations['attributes']['combined_'+key]=Attribute('combined_'+key, annotations['tags'][e_t_mapper[key]],
                                                                'Combined', '_'.join(attribute_mapper[key]))
        return annotations

    def _get_text(self):
        """Return the text in the corresponding txt file."""
        path = self.path.replace('.ann', '.txt')
        with open(path) as text_file:
            text = text_file.read()
        return text

    def search_by_id(self, key):
        """Search by id among both tags and attributes."""
        try:
            return self.annotations['tags'][key]
        except KeyError():
            try:
                return self.annotations['attributes'][key]
            except KeyError():
                return None

class Measures(object):
    """Abstract methods and var to evaluate."""

    def __init__(self, tp=0, tn=0, fp=0, fn=0):
        """Initizialize."""
        assert type(tp) == int
        assert type(tn) == int
        assert type(fp) == int
        assert type(fn) == int
        self.tp = tp
        self.tn = tn
        self.fp = fp
        self.fn = fn

    def precision(self):
        """Compute Precision score."""
        try:
            return self.tp / (self.tp + self.fp)
        except ZeroDivisionError:
            return 0.0

    def recall(self):
        """Compute Recall score."""
        try:
            return self.tp / (self.tp + self.fn)
        except ZeroDivisionError:
            return 0.0

    def f_score(self, beta=1):
        """Compute F1-measure score."""
        assert beta > 0.
        try:
            num = (1 + beta**2) * (self.precision() * self.recall())
            den = beta**2 * (self.precision() + self.recall())
            return num / den
        except ZeroDivisionError:
            return 0.0

    def f1(self):
        """Compute the F1-score (beta=1)."""
        return self.f_score(beta=1)

    def specificity(self):
        """Compute Specificity score."""
        try:
            return self.tn / (self.fp + self.tn)
        except ZeroDivisionError:
            return 0.0

    def sensitivity(self):
        """Compute Sensitivity score."""
        return self.recall()

    def auc(self):
        """Compute AUC score."""
        return (self.sensitivity() + self.specificity()) / 2

class SingleEvaluator(object):
    """Evaluate two single files."""

    def _remove_duplicate_tags(self, tags):
        skip_indices=set()
        dedup_tags=[]
        for i in range(0, len(tags)):
            if i in skip_indices:
                continue
            for j in range(i+1, len(tags)):
                if tags[i].equals(tags[j]):
                    skip_indices.add(j)
            dedup_tags.append(tags[i])
        return dedup_tags

    def _remove_multiple_overlapping_tags(self, gol, sys, mode):
        gol_matched = []
        sys_check_tag=deepcopy(sys)
        for s in sys:
            for g in gol:
                if (g.equals(s,mode)):
                    if g not in gol_matched:
                        gol_matched.append(g)
                    else:
                        if s in sys_check_tag:
                            sys_check_tag.remove(s)
        return sys_check_tag

    def _get_tp(self, sys, gol, mode):
        matched = set()
        sys_matched=set()
        for i in range(0, len(gol)):
            g=gol[i]
            for s in sys:
                if g.equals(s, mode) and s.rid not in sys_matched:
                    matched.add(g.rid)
                    sys_matched.add(s.rid)
                    break
        return len(matched)

        #len({g.rid for g in gol for s in sys if g.equals(s, mode)})

        

    def __init__(self, doc1, doc2, track, mode='strict', key=None, verbose=False):
        """Initialize."""
        assert isinstance(doc1, RecordTrack1)
        assert isinstance(doc2, RecordTrack1)
        assert mode in ('strict', 'lenient')
        assert doc1.basename == doc2.basename
        self.scores = {'tags': {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0},
                       'attributes': {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}}
        self.doc1 = doc1
        self.doc2 = doc2
        if key:
            gol = [t for t in doc1.tags.values() if t.ttype == key]
            sys = [t for t in doc2.tags.values() if t.ttype == key]
        else:
            gol = [t for t in doc1.tags.values() if t.ttype != 'Drug']
            sys = [t for t in doc2.tags.values() if t.ttype != 'Drug']
        
        sys_check_tag = self._remove_duplicate_tags(sys)
        gol_check_tag = self._remove_duplicate_tags(gol)
        #now evaluate
        #self.scores['tags']['tp'] = len({g.tid for g in gol_check_tag for s in sys_check_tag if g.equals(s, mode)})
        self.scores['tags']['tp'] = self._get_tp(sys_check_tag, gol_check_tag, mode)
        self.scores['tags']['fp'] = max(len({s.rid for s in sys_check_tag}) - self.scores['tags']['tp'],0)
        self.scores['tags']['fn'] = max(len({g.rid for g in gol_check_tag}) - self.scores['tags']['tp'],0)
        self.scores['tags']['tn'] = 0

        if verbose and track == 1:
            tps = {s for s in sys for g in gol if g.equals(s, mode)}
            fps = set(sys) - tps
            fns = set()
            for g in gol:
                if not len([s for s in sys if s.equals(g, mode)]):
                    fns.add(g)
            for e in fps:
                print('FP: ' + str(e))
            for e in fns:
                print('FN:' + str(e))
        if track == 1:
            if key:
                gol = [r for r in doc1.attributes.values() if r.rtype == key]
                sys = [r for r in doc2.attributes.values() if r.rtype == key]
            else:
                gol = [r for r in doc1.attributes.values() if r.rtype != 'Combined']
                sys = [r for r in doc2.attributes.values() if r.rtype != 'Combined']

            #now evaluate
            #self.scores['attributes']['tp'] = len({g.rid for g in gol for s in sys if g.equals(s, mode)})
            self.scores['attributes']['tp'] = self._get_tp(sys, gol, mode)
            self.scores['attributes']['fp'] = max((len({s.rid for s in sys}) - self.scores['attributes']['tp']),0)
            self.scores['attributes']['fn'] = max((len({g.rid for g in gol}) - self.scores['attributes']['tp']),0)
            self.scores['attributes']['tn'] = 0
            if verbose:
                tps = {s for s in sys for g in gol if g.equals(s, mode)}
                fps = set(sys) - tps
                fns = set()
                for g in gol:
                    if not len([s for s in sys if s.equals(g, mode)]):
                        fns.add(g)
                for e in fps:
                    print('FP: ' + str(e))
                for e in fns:
                    print('FN:' + str(e))

class MultipleEvaluator(object):
    """Evaluate two sets of files."""

    def __init__(self, corpora, tag_type=None, mode='strict',
                 verbose=False):
        """Initialize."""
        assert isinstance(corpora, Corpora)
        assert mode in ('strict', 'lenient')
        self.scores = None
        self.track1(corpora, tag_type, mode, verbose)

    def track1(self, corpora, tag_type=None, mode='strict', verbose=False):
        """Compute measures for Track 1."""
        self.scores = {'tags': {'tp': 0,
                                'fp': 0,
                                'fn': 0,
                                'tn': 0,
                                'micro': {'precision': 0,
                                          'recall': 0,
                                          'f1': 0}},
                       'attributes': {'tp': 0,
                                     'fp': 0,
                                     'fn': 0,
                                     'tn': 0,
                                     'micro': {'precision': 0,
                                               'recall': 0,
                                               'f1': 0}}}
        self.tags = ('Drug', 'Disposition', 'NoDisposition', 'Undetermined')
        self.attributes = ('Action', 'Temporality', 'Certainty', 'Actor', 'Negation', 'Combined')
        for g, s in corpora.docs:
            evaluator = SingleEvaluator(g, s, 1, mode, tag_type, verbose=verbose)
            for target in ('tags', 'attributes'):
                for score in ('tp', 'fp', 'fn'):
                    self.scores[target][score] += evaluator.scores[target][score]
                measures = Measures(tp=evaluator.scores[target]['tp'],
                                    fp=evaluator.scores[target]['fp'],
                                    fn=evaluator.scores[target]['fn'],
                                    tn=evaluator.scores[target]['tn'])
        for target in ('tags', 'attributes'):
            measures = Measures(tp=self.scores[target]['tp'],
                                fp=self.scores[target]['fp'],
                                fn=self.scores[target]['fn'],
                                tn=self.scores[target]['tn'])
            for key in self.scores[target]['micro'].keys():
                fn = getattr(measures, key)
                self.scores[target]['micro'][key] = fn()

class Corpora(object):
    def __init__(self, folder1, folder2):
        file_ext = '*.ann'
        self.folder1 = folder1
        self.folder2 = folder2
        files1 = set([os.path.basename(f) for f in glob.glob(
            os.path.join(folder1, file_ext))])
        files2 = set([os.path.basename(f) for f in glob.glob(
            os.path.join(folder2, file_ext))])
        common_files = files1 & files2     # intersection
        if not common_files:
            print('ERROR: None of the files match.')
        else:
            if files1 - common_files:
                print('Files skipped in {}:'.format(self.folder1))
                print(', '.join(sorted(list(files1 - common_files))))
            if files2 - common_files:
                print('Files skipped in {}:'.format(self.folder2))
                print(', '.join(sorted(list(files2 - common_files))))
        self.docs = []
        for file in common_files:
                g = RecordTrack1(os.path.join(self.folder1, file))
                s = RecordTrack1(os.path.join(self.folder2, file))
                self.docs.append((g, s))

def evaluate(corpora, mode='strict', verbose=False):
    """Run the evaluation by considering only files in the two folders."""
    assert mode in ('strict', 'lenient')
    evaluator_s = MultipleEvaluator(corpora, verbose=verbose)
    evaluator_l = MultipleEvaluator(corpora, mode='lenient', verbose=verbose)
    print()
    print('{:*^70}'.format(' Evaluation n2c2 2022 Track 1 '))
    print('{:*^70}'.format(' Contextualized Medication Event Extraction '))
    
    print()
    print('{:*^70}'.format(' Medication Extraction '))
    print('{:20}  {:-^22}    {:-^22}'.format('', ' strict ', ' lenient '))
    print('{:20}  {:6}  {:6}  {:6}    {:6}  {:6}  {:6}'.format('', 'Prec.',
                                                                'Rec.',
                                                                'F(b=1)',
                                                                'Prec.',
                                                                'Rec.',
                                                                'F(b=1)'))
    s_macro_precision, s_macro_recall, s_macro_f1=[], [], []
    l_macro_precision, l_macro_recall, l_macro_f1=[], [], []
    for tag in ['Drug']:
        evaluator_tag_s = MultipleEvaluator(corpora, tag, verbose=verbose)
        evaluator_tag_l = MultipleEvaluator(corpora, tag, mode='lenient', verbose=verbose)
        print('{:>20}  {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}  {:<5.4f}'.format(
            tag.capitalize(),
            evaluator_tag_s.scores['tags']['micro']['precision'],
            evaluator_tag_s.scores['tags']['micro']['recall'],
            evaluator_tag_s.scores['tags']['micro']['f1'],
            evaluator_tag_l.scores['tags']['micro']['precision'],
            evaluator_tag_l.scores['tags']['micro']['recall'],
            evaluator_tag_l.scores['tags']['micro']['f1']))
    print()
    print()
    print('{:*^70}'.format(' Event Classification '))
    print('{:20}  {:-^22}    {:-^22}'.format('', ' strict ', ' lenient '))
    print('{:20}  {:6}  {:6}  {:6}    {:6}  {:6}  {:6}'.format('', 'Prec.',
                                                                'Rec.',
                                                                'F(b=1)',
                                                                'Prec.',
                                                                'Rec.',
                                                                'F(b=1)'))
    s_macro_precision, s_macro_recall, s_macro_f1=[], [], []
    l_macro_precision, l_macro_recall, l_macro_f1=[], [], []
    for tag in ['Disposition', 'NoDisposition', 'Undetermined']:
        evaluator_tag_s = MultipleEvaluator(corpora, tag, verbose=verbose)
        evaluator_tag_l = MultipleEvaluator(corpora, tag, mode='lenient', verbose=verbose)
        print('{:>20}  {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}  {:<5.4f}'.format(
            tag.capitalize(),
            evaluator_tag_s.scores['tags']['micro']['precision'],
            evaluator_tag_s.scores['tags']['micro']['recall'],
            evaluator_tag_s.scores['tags']['micro']['f1'],
            evaluator_tag_l.scores['tags']['micro']['precision'],
            evaluator_tag_l.scores['tags']['micro']['recall'],
            evaluator_tag_l.scores['tags']['micro']['f1']))
        s_macro_precision.append(evaluator_tag_s.scores['tags']['micro']['precision'])
        s_macro_recall.append( evaluator_tag_s.scores['tags']['micro']['recall'])
        s_macro_f1.append(evaluator_tag_s.scores['tags']['micro']['f1'])
        l_macro_precision.append(evaluator_tag_l.scores['tags']['micro']['precision'])
        l_macro_recall.append(evaluator_tag_l.scores['tags']['micro']['recall'])
        l_macro_f1.append(evaluator_tag_l.scores['tags']['micro']['f1'])
    print('{:>20}  {:-^48}'.format('', ''))
    print('{:>20}  {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}  {:<5.4f}'.format(
        'Overall (micro)',
        evaluator_s.scores['tags']['micro']['precision'],
        evaluator_s.scores['tags']['micro']['recall'],
        evaluator_s.scores['tags']['micro']['f1'],
        evaluator_l.scores['tags']['micro']['precision'],
        evaluator_l.scores['tags']['micro']['recall'],
        evaluator_l.scores['tags']['micro']['f1']))
    print('{:>20}  {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}  {:<5.4f}'.format(
        'Overall (macro)',
        statistics.mean(s_macro_precision),
        statistics.mean(s_macro_recall),
        statistics.mean(s_macro_f1),
        statistics.mean(l_macro_precision),
        statistics.mean(l_macro_recall),
        statistics.mean(l_macro_f1)))
    print()

    s_macro_precision, s_macro_recall, s_macro_f1=[], [], []
    l_macro_precision, l_macro_recall, l_macro_f1=[], [], []
    print()
    print('{:*^70}'.format(' Context Classification '))
    print('{:20}  {:-^22}    {:-^22}'.format('', ' strict ', ' lenient '))
    print('{:20}  {:6}  {:6}  {:6}    {:6}  {:6}  {:6}'.format('', 'Prec.',
                                                            'Rec.',
                                                            'F(b=1)',
                                                            'Prec.',
                                                            'Rec.',
                                                            'F(b=1)'))
    for rel in evaluator_s.attributes:
        if rel=='Combined':
            continue
        evaluator_tag_s = MultipleEvaluator(corpora, rel, mode='strict', verbose=verbose)
        evaluator_tag_l = MultipleEvaluator(corpora, rel, mode='lenient', verbose=verbose)
        print('{:>20}  {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}  {:<5.4f}'.format(
            '{}'.format(rel),
            evaluator_tag_s.scores['attributes']['micro']['precision'],
            evaluator_tag_s.scores['attributes']['micro']['recall'],
            evaluator_tag_s.scores['attributes']['micro']['f1'],
            evaluator_tag_l.scores['attributes']['micro']['precision'],
            evaluator_tag_l.scores['attributes']['micro']['recall'],
            evaluator_tag_l.scores['attributes']['micro']['f1']))
        s_macro_precision.append(evaluator_tag_s.scores['attributes']['micro']['precision'])
        s_macro_recall.append( evaluator_tag_s.scores['attributes']['micro']['recall'])
        s_macro_f1.append(evaluator_tag_s.scores['attributes']['micro']['f1'])
        l_macro_precision.append(evaluator_tag_l.scores['attributes']['micro']['precision'])
        l_macro_recall.append(evaluator_tag_l.scores['attributes']['micro']['recall'])
        l_macro_f1.append(evaluator_tag_l.scores['attributes']['micro']['f1'])
    print('{:>20}  {:-^48}'.format('', ''))
    print('{:>20}  {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}  {:<5.4f}'.format(
        'Overall (micro)',
        evaluator_s.scores['attributes']['micro']['precision'],
        evaluator_s.scores['attributes']['micro']['recall'],
        evaluator_s.scores['attributes']['micro']['f1'],
        evaluator_l.scores['attributes']['micro']['precision'],
        evaluator_l.scores['attributes']['micro']['recall'],
        evaluator_l.scores['attributes']['micro']['f1']))
    print('{:>20}  {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}  {:<5.4f}'.format(
        'Overall (macro)',
        statistics.mean(s_macro_precision),
        statistics.mean(s_macro_recall),
        statistics.mean(s_macro_f1),
        statistics.mean(l_macro_precision),
        statistics.mean(l_macro_recall),
        statistics.mean(l_macro_f1)))
    print()
    print()
    print('{:20}  {:-^22}    {:-^22}'.format('', ' strict ', ' lenient '))
    print('{:20}  {:6}  {:6}  {:6}    {:6}  {:6}  {:6}'.format('', 'Prec.',
                                                            'Rec.',
                                                            'F(b=1)',
                                                            'Prec.',
                                                            'Rec.',
                                                            'F(b=1)'))
    evaluator_tag_s = MultipleEvaluator(corpora, 'Combined', mode='strict', verbose=verbose)
    evaluator_tag_l = MultipleEvaluator(corpora, 'Combined', mode='lenient', verbose=verbose)
    print('{:>20}  {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}  {:<5.4f}'.format(
        '{}'.format(rel),
        evaluator_tag_s.scores['attributes']['micro']['precision'],
        evaluator_tag_s.scores['attributes']['micro']['recall'],
        evaluator_tag_s.scores['attributes']['micro']['f1'],
        evaluator_tag_l.scores['attributes']['micro']['precision'],
        evaluator_tag_l.scores['attributes']['micro']['recall'],
        evaluator_tag_l.scores['attributes']['micro']['f1']))
    print()
    print()                                                       
    print('{:20}{:^48}'.format('', '  {} files evaluated  '.format(len(corpora.docs))))

def main(f1, f2, verbose):
    corpora = Corpora(f1, f2)
    if corpora.docs:
        evaluate(corpora, verbose=verbose)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='n2c2: Evaluation script for Track 1')
    parser.add_argument('folder1', help='First data folder path (gold)')
    parser.add_argument('folder2', help='Second data folder path (system)')
    args = parser.parse_args()
    main(os.path.abspath(args.folder1), os.path.abspath(args.folder2), False)