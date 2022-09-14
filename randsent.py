#!/usr/bin/env python3
"""
601.465/665 — Natural Language Processing
Assignment 1: Designing Context-Free Grammars

Assignment written by Jason Eisner
Modified by Kevin Duh
Re-modified by Alexandra DeLucia

Code template written by Alexandra DeLucia,
based on the submitted assignment with Keith Harrigian
and Carlos Aguirre Fall 2019
"""
import os
import re
import sys
import random
import argparse


# Want to know what command-line arguments a program allows?
# Commonly you can ask by passing it the --help option, like this:
#     python randsent.py --help
# This is possible for any program that processes its command-line
# arguments using the argparse module, as we do below.
#
# NOTE: When you use the Python argparse module, parse_args() is the
# traditional name for the function that you create to analyze the
# command line.  Parsing the command line is different from parsing a
# natural-language sentence.  It's easier.  But in both cases,
# "parsing" a string means identifying the elements of the string and
# the roles they play.

def parse_args():
    """
    Parse command-line arguments.

    Returns:
        args (an argparse.Namespace): Stores command-line attributes
    """
    # Initialize parser
    parser = argparse.ArgumentParser(description="Generate random sentences from a PCFG")
    # Grammar file (required argument)
    parser.add_argument(
        "-g",
        "--grammar",
        type=str, required=True,
        help="Path to grammar file",
    )
    # Start symbol of the grammar
    parser.add_argument(
        "-s",
        "--start_symbol",
        type=str,
        help="Start symbol of the grammar (default is ROOT)",
        default="ROOT",
    )
    # Number of sentences
    parser.add_argument(
        "-n",
        "--num_sentences",
        type=int,
        help="Number of sentences to generate (default is 1)",
        default=1,
    )
    # Max number of nonterminals to expand when generating a sentence
    parser.add_argument(
        "-M",
        "--max_expansions",
        type=int,
        help="Max number of nonterminals to expand when generating a sentence",
        default=450,
    )
    # Print the derivation tree for each generated sentence
    parser.add_argument(
        "-t",
        "--tree",
        action="store_true",
        help="Print the derivation tree for each generated sentence",
        default=False,
    )
    return parser.parse_args()


class Grammar:
    def __init__(self, grammar_file):
        """
        Context-Free Grammar (CFG) Sentence Generator

        Args:
            grammar_file (str): Path to a .gr grammar file

        Returns:
            self
        """
        # Parse the input grammar file
        self.rules = None
        self._load_rules_from_file(grammar_file)

    def _load_rules_from_file(self, grammar_file):
        """
        Read grammar file and store its rules in self.rules

        Args:
            grammar_file (str): Path to the raw grammar file
        """
        ##Siwei & Shreayan
        rules = {}
        file = open(grammar_file, 'r')

        for line in file.readlines():

            # traverse grammar file linewise and create the rules dict with odds
            if line[0].isdigit():
                line = line.strip("\n")
                weight, LHS, RHS = re.split("\t", line)
                weight = float(weight)

                pattern = "  " + ".*"
                RHS = re.sub(pattern, '', RHS)

                if LHS not in rules.keys():
                    # if symbol is not existing in rules, then create a new dictionary along with its odds
                    rules[LHS] = {}

                # set the odds / weights of the symbol
                rules[LHS][RHS] = weight

        self.rules = rules
        ##Siwei & Shreayan

    def parse_symbols(self, symbol, derivation_tree, num_expansions):
        """
        Function to parse the symbols in the ruleset
        Args:
            symbol: the symbol to be parsed
            derivation_tree: if true, the returned string will represent
                the tree (using bracket notation) that records how the sentence
                was derived
            num_expansions: the number of expansions in the tree to keep a track on

        Returns:
            str: the string containing the parsed symbols
        """
        sentence = ""

        if num_expansions <= 0 and any(ch.isupper() for ch in symbol):
            # for very large sentences, return ... when the limit is reached
            return "... "

        if symbol in self.rules.keys():
            # start with max_expansions given by the user and keep decrementing each time symbol is expanded
            self.num_expansions -= 1

            # if the symbol is found in the grammar ruleset, recursively parse it

            if derivation_tree:
                # adding the tree representation and parenthesis to show provenance
                sentence += "(" + symbol + " "

            RHS = list(self.rules[symbol].keys())
            odds = list(self.rules[symbol].values())

            # select a random expansion with the given weights
            expansion = random.choices(RHS, odds, k=1)[0]

            if any(ch.isupper() for ch in expansion):

                # if the symbol contains any nonterminal symbols like S, NP, VP, is it true that S ?
                # split the expansion and look for other symbols in it recursively - nonterminal symbols
                for symbol in expansion.split(" "):
                    sentence += self.parse_symbols(symbol=symbol,
                                                   derivation_tree=derivation_tree,
                                                   num_expansions=self.num_expansions)
                if derivation_tree:
                    # close the parentheses of the above symbol
                    sentence += ")"
            else:
                # otherwise just add the expansion to the sentence as it is (chief of staff, and multi word symbols)
                sentence += expansion + " "
                if derivation_tree:
                    # adding the tree representation and parenthesis to show provenance
                    sentence += ")"

        else:
            # otherwise just add the symbol to the sentence as it is - terminal symbols
            sentence += symbol + " "

        return sentence

    def sample(self, derivation_tree, max_expansions, start_symbol):
        """
        Sample a random sentence from this grammar

        Args:
            derivation_tree (bool): if true, the returned string will represent
                the tree (using bracket notation) that records how the sentence
                was derived

            max_expansions (int): max number of nonterminal expansions we allow

            start_symbol (str): start symbol to generate from

        Returns:
            str: the random sentence or its derivation tree
        """
        ## Siwei & Shreayan
        # class variable to keep a track on the number expansions when user enters multiple sentences
        self.num_expansions = max_expansions

        # decrement number of expansions each time the recursive function is called
        sentence = self.parse_symbols(start_symbol, derivation_tree, self.num_expansions)
        return sentence


####################
### Main Program
####################
def main():
    # Parse command-line options
    args = parse_args()

    # Initialize Grammar object
    grammar = Grammar(args.grammar)

    # Generate sentences
    for i in range(args.num_sentences):
        # Use Grammar object to generate sentence
        sentence = grammar.sample(
            derivation_tree=args.tree,
            max_expansions=args.max_expansions,
            start_symbol=args.start_symbol
        )

        # Print the sentence with the specified format.
        # If it's a tree, we'll pipe the output through the prettyprint script.
        if args.tree:
            prettyprint_path = os.path.join(os.getcwd(), 'prettyprint')
            t = os.system(f"echo '{sentence}' | perl {prettyprint_path}")
        else:
            print(sentence)


if __name__ == "__main__":
    main()
