# -*- coding: utf-8 -*-
from collections import defaultdict
from sklearn.metrics import classification_report
import argparse
import math
import re
import json
from pprint import pprint


def process_input_text(input_text):
    word2digit = {}
    for line in input_text.strip().split('\n'):
        word = line.strip().replace(' ', '')
        i = 0
        segments = []
        for span in re.finditer('\s', line.strip()):
            p = span.start()
            segments.append(line[i:p].strip())
            i = p + 1
        segments.append(line[i:].strip())
        digits = '1'.join(['0' * (len(segment) - 1) for segment in segments ])
        word2digit[word] = digits
    return word2digit


def process_acceptable_theories(raw_theories):
    id2rules = {}
    for line in raw_theories:
        id, total, *rules = line
        size = int(math.log2(total))
        id2rules[id] = [
            bin(rule)[2:].zfill(size)
            for rule in rules
        ]
    return id2rules

def parse_gold_text(gold_text, theories):
    word2gold = {}
    word2rule2digit = {}
    lines = gold_text.split('\n')
    if lines[0].startswith('1'):
        lines = ['\n'] + lines  # Add empty line for 0th word
    
    for i, line in enumerate(lines):
        line = line.split(';')[0].rstrip()  # Remove comments
        if len(line) and line[0].isdigit():
            seg_id, segment_str = line.strip().split()
            rule_str = lines[i - 1].split(';')[0].rstrip()[len(seg_id) + 1:]
            rule_str += ' ' * (len(segment_str) - len(rule_str))
            i = 0
            gold_digits = ''
            rule_digit_index = defaultdict(list)
            word = segment_str[0]
            is_previous_boundary = False
            for char, rule_id in zip(segment_str[1:], rule_str[1:]):
                match char:
                    case '+' | '-' | '/':
                        gold_digits += '1'
                        is_previous_boundary = True
                        
                    case '.':
                        assert len(rule_id.strip()), f"Theory rule not aligned with gold text: {rule_id} - {word} in {segment_str}"
                        gold_digits += '?'
                        if rule_id in rule_digit_index and len(rule_digit_index[rule_id][-1]) < len(theories[rule_id][0]):
                            rule_digit_index[rule_id][-1].append(len(gold_digits) - 1)
                        else:
                            rule_digit_index[rule_id].append([len(gold_digits) - 1])
                        is_previous_boundary = True
                        
                    case _:
                        if not is_previous_boundary:
                            gold_digits += '0'
                        word += char
                        is_previous_boundary = False
                        
            word2gold[word] = gold_digits
            if len(rule_digit_index):
                word2rule2digit[word] = rule_digit_index
    rule2word2digit = {}
    for word, rule_digit_index in word2rule2digit.items():
        for rule_id, digit_indices in rule_digit_index.items():
            if rule_id not in rule2word2digit:
                rule2word2digit[rule_id] = {}
            rule2word2digit[rule_id][word] = digit_indices
    return word2gold, rule2word2digit


def get_most_suppported_rule(pred_dict, rule2word2digit):
    support_dict = {
        id: {digit: 0 for digit in digits} 
        for id, digits in theories.items() 
    }
    for rule_id, word_dict in rule2word2digit.items():
        for word, digit_groups in word_dict.items():
            if word not in pred_dict:
                continue
            pred = pred_dict[word]
            for group in digit_groups:
                rule_digits = ''.join([pred[i] for i in group])
                if rule_digits in support_dict[rule_id]:
                    support_dict[rule_id][rule_digits] += 1
    picked_rule = {
        id: max(digits, key=digits.get) 
        for id, digits in support_dict.items()
    }
    return picked_rule

def apply_rule(gold_dict, picked_rule, rule2word2digit):
    filled_gold_dict = gold_dict.copy()
    for rule_id, word2digit in rule2word2digit.items():
        if rule_id not in picked_rule:
            continue
        for word, digit_groups in word2digit.items():
            if word not in gold_dict:
                continue
            gold_digit_arr = [_ for _ in filled_gold_dict[word]]
            for group in digit_groups:
                for i, digit in zip(group, picked_rule[rule_id]):
                    gold_digit_arr[i] = digit
            filled_gold_dict[word] = ''.join(gold_digit_arr)
    return filled_gold_dict

def evaluate(gold_dict, pred_dict):
    gold_labels = []
    pred_labels = []
    
    for word in gold_dict:
        if word not in pred_dict:
            continue
        assert len(gold_dict[word]) == len(pred_dict[word]), f"Length mismatch for word '{word}': {len(gold_dict[word])} vs {len(pred_dict[word])}"
        gold_labels.extend([_ for _ in gold_dict[word]])
        pred_labels.extend([_ for _ in pred_dict[word]])
        if '?' in gold_dict[word]:
            print(f"Warning: '?' found in gold labels for word '{word}': {gold_dict[word]}")
    print(classification_report(gold_labels, pred_labels, digits=5))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='A script to evaluate segmented words')
    argparser.add_argument('--gold', type=str, required=True, help='The path to the gold file')
    argparser.add_argument('--pred', type=str, required=True, help='The path to the predicted file')
    argparser.add_argument('--theories', type=str, required=True, help='The path to the theories json file')
    args = argparser.parse_args()
    
    gold_text = open(args.gold, 'r', encoding='utf-8').read() 
    pred_text = open(args.pred, 'r', encoding='utf-8').read() 
    raw_theories = json.load(open(args.theories, 'r', encoding='utf-8')) # fi.json
    
    pred_dict = process_input_text(pred_text)
    theories = process_acceptable_theories(raw_theories)
    
    raw_gold_dict, rule2word2digit = parse_gold_text(gold_text, theories)
    # print(rule2word2digit)
    try:
        assert ' ' not in rule2word2digit, "Labels not aligned with words, please check the gold file."
    except AssertionError as e:
        print(e)
        pprint(rule2word2digit[' '])
        exit(1)
    
    picked_rule = get_most_suppported_rule(pred_dict, rule2word2digit)
    filled_gold_dict = apply_rule(raw_gold_dict, picked_rule, rule2word2digit)
    assert all('?' not in digit for digit in filled_gold_dict.values()), "There are still '?' in the filled gold dictionary."
    evaluate(filled_gold_dict, pred_dict)