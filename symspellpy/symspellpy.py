"""
.. module:: symspellpy
   :synopsis: Module for Symmetric Delete spelling correction algorithm.
"""
from collections import defaultdict, namedtuple
from enum import Enum
import gzip
from itertools import cycle
import math
import os.path
import pickle
import re
import sys

from symspellpy.editdistance import DistanceAlgorithm, EditDistance
import symspellpy.helpers as helpers

class Verbosity(Enum):
    TOP = 0  
    CLOSEST = 1
    ALL = 2  

class SymSpell(object):

    def __init__(self, max_dictionary_edit_distance=2, prefix_length=7,
                 count_threshold=1):
        if max_dictionary_edit_distance < 0:
            raise ValueError("max_dictionary_edit_distance cannot be "
                             "negative")
        if (prefix_length < 1
                or prefix_length <= max_dictionary_edit_distance):
            raise ValueError("prefix_length cannot be less than 1 or "
                             "smaller than max_dictionary_edit_distance")
        if count_threshold < 0:
            raise ValueError("count_threshold cannot be negative")
        self._words = defaultdict(int)
        self._deletes = defaultdict(list)
        self._max_dictionary_edit_distance = max_dictionary_edit_distance
        self._prefix_length = prefix_length
        self._count_threshold = count_threshold
        self._distance_algorithm = DistanceAlgorithm.DAMERUAUOSA
        self._max_length = 0
        self._replaced_words = dict()

    def create_dictionary_entry(self, key, count):
        self._words[key] += count

        if len(key) > self._max_length:
            self._max_length = len(key)

        edits = self._edits_prefix(key)
        for delete in edits:
            self._deletes[delete].append(key)

        return True

    def delete_dictionary_entry(self, key):
        if key not in self._words:
            return False
        del self._words[key]

        if len(key) == self._max_length:
            self._max_length = max(map(len, self._words.keys()))

        # create deletes
        edits = self._edits_prefix(key)
        for delete in edits:
            self._deletes[delete].remove(key)
        return True

    def load_dictionary(self, corpus, term_index, count_index,
                        separator=" ", encoding=None):
        if not os.path.exists(corpus):
            return False
        with gzip.open(corpus, "rt", encoding=encoding) as infile:
            for line in infile:
                line_parts = line.rstrip().split(separator)
                if len(line_parts) >= 2:
                    key = line_parts[term_index]
                    count = helpers.try_parse_int64(line_parts[count_index])
                    if count is not None:
                        self.create_dictionary_entry(key, count)
        return True

    def create_dictionary(self, corpus, encoding=None):
        if isinstance(corpus, str):
            if not os.path.exists(corpus):
                return False
            with gzip.open(corpus, "rt", encoding=encoding) as infile:
                for line in infile:
                    for key in self._parse_words(line):
                        self.create_dictionary_entry(key, 1)
        else:
            for line in corpus:
                for key in self._parse_words(line):
                    self.create_dictionary_entry(key, 1)
        return True

    def save_pickle_stream(self, stream):
        pickle_data = {
            "deletes": self._deletes,
            "words": self._words,
            "max_length": self._max_length,
            "data_version": self.data_version
        }
        pickle.dump(pickle_data, stream)

    def save_pickle(self, filename, compressed=True):
        with (gzip.open if compressed else open)(filename, "wb") as f:
            self.save_pickle_stream(f)

    def load_pickle_stream(self, stream):
        pickle_data = pickle.load(stream)
        if ("data_version" not in pickle_data
                or pickle_data["data_version"] != self.data_version):
            return False
        self._deletes = pickle_data["deletes"]
        self._words = pickle_data["words"]
        self._max_length = pickle_data["max_length"]
        return True

    def load_pickle(self, filename, compressed=True):
        with (gzip.open if compressed else open)(filename, "rb") as f:
            return self.load_pickle_stream(f)

    def lookup(self, phrase, verbosity, max_edit_distance=None,
               include_unknown=False, ignore_token=None):

        if max_edit_distance is None:
            max_edit_distance = self._max_dictionary_edit_distance
        if max_edit_distance > self._max_dictionary_edit_distance:
            raise ValueError("Distance too large")
        suggestions = list()
        phrase_len = len(phrase)

        def early_exit():
            if include_unknown and not suggestions:
                suggestions.append(SuggestItem(phrase, max_edit_distance + 1,
                                               0))
            return suggestions
        # early exit - word is too big to possibly match any words
        if phrase_len - max_edit_distance > self._max_length:
            return early_exit()

        # quick look for exact match
        suggestion_count = 0
        if phrase in self._words:
            suggestion_count = self._words[phrase]
            suggestions.append(SuggestItem(phrase, 0, suggestion_count))
            # early exit - return exact match, unless caller wants all
            # matches
            if verbosity != Verbosity.ALL:
                return early_exit()

        if (ignore_token is not None
                and re.match(ignore_token, phrase) is not None):
            suggestion_count = 1
            suggestions.append(SuggestItem(phrase, 0, suggestion_count))
            # early exit - return exact match, unless caller wants all
            # matches
            if verbosity != Verbosity.ALL:
                return early_exit()

        # early termination, if we only want to check if word in
        # dictionary or get its frequency e.g. for word segmentation
        if max_edit_distance == 0:
            return early_exit()

        considered_deletes = set()
        considered_suggestions = set()
        # we considered the phrase already in the
        # 'phrase in self._words' above
        considered_suggestions.add(phrase)

        max_edit_distance_2 = max_edit_distance
        candidate_pointer = 0
        candidates = list()

        # add original prefix
        phrase_prefix_len = phrase_len
        if phrase_prefix_len > self._prefix_length:
            phrase_prefix_len = self._prefix_length
            candidates.append(phrase[: phrase_prefix_len])
        else:
            candidates.append(phrase)
        distance_comparer = EditDistance(self._distance_algorithm)
        while candidate_pointer < len(candidates):
            candidate = candidates[candidate_pointer]
            candidate_pointer += 1
            candidate_len = len(candidate)
            len_diff = phrase_prefix_len - candidate_len

            # early termination: if candidate distance is already
            # higher than suggestion distance, than there are no better
            # suggestions to be expected
            if len_diff > max_edit_distance_2:
                # skip to next candidate if Verbosity.ALL, look no
                # further if Verbosity.TOP or CLOSEST (candidates are
                # ordered by delete distance, so none are closer than
                # current)
                if verbosity == Verbosity.ALL:
                    continue
                break

            if candidate in self._deletes:
                dict_suggestions = self._deletes[candidate]
                for suggestion in dict_suggestions:
                    if suggestion == phrase:
                        continue
                    suggestion_len = len(suggestion)
                    # phrase and suggestion lengths
                    # diff > allowed/current best distance
                    if (abs(suggestion_len - phrase_len) > max_edit_distance_2
                            # suggestion must be for a different delete
                            # string, in same bin only because of hash
                            # collision
                            or suggestion_len < candidate_len
                            # if suggestion len = delete len, then it
                            # either equals delete or is in same bin
                            # only because of hash collision
                            or (suggestion_len == candidate_len
                                and suggestion != candidate)):
                        continue
                    suggestion_prefix_len = min(suggestion_len,
                                                self._prefix_length)
                    if (suggestion_prefix_len > phrase_prefix_len
                            and suggestion_prefix_len - candidate_len > max_edit_distance_2):
                        continue
                    # True Damerau-Levenshtein Edit Distance: adjust
                    # distance, if both distances>0
                    # We allow simultaneous edits (deletes) of
                    # max_edit_distance on on both the dictionary and
                    # the phrase term. For replaces and adjacent
                    # transposes the resulting edit distance stays
                    # <= max_edit_distance. For inserts and deletes the
                    # resulting edit distance might exceed
                    # max_edit_distance. To prevent suggestions of a
                    # higher edit distance, we need to calculate the
                    # resulting edit distance, if there are
                    # simultaneous edits on both sides.
                    # Example: (bank==bnak and bank==bink, but
                    # bank!=kanb and bank!=xban and bank!=baxn for
                    # max_edit_distance=1). Two deletes on each side of
                    # a pair makes them all equal, but the first two
                    # pairs have edit distance=1, the others edit
                    # distance=2.
                    distance = 0
                    min_distance = 0
                    if candidate_len == 0:
                        # suggestions which have no common chars with
                        # phrase (phrase_len<=max_edit_distance &&
                        # suggestion_len<=max_edit_distance)
                        distance = max(phrase_len, suggestion_len)
                        if (distance > max_edit_distance_2
                                or suggestion in considered_suggestions):
                            continue
                    elif suggestion_len == 1:
                        distance = (phrase_len
                                    if phrase.index(suggestion[0]) < 0
                                    else phrase_len - 1)
                        if (distance > max_edit_distance_2
                                or suggestion in considered_suggestions):
                            continue
                    # number of edits in prefix ==maxediddistance AND
                    # no identical suffix, then
                    # editdistance>max_edit_distance and no need for
                    # Levenshtein calculation
                    # (phraseLen >= prefixLength) &&
                    # (suggestionLen >= prefixLength)
                    else:
                        # handles the shortcircuit of min_distance
                        # assignment when first boolean expression
                        # evaluates to False
                        if self._prefix_length - max_edit_distance == candidate_len:
                            min_distance = (min(phrase_len, suggestion_len) -
                                            self._prefix_length)
                        else:
                            min_distance = 0
                        # pylint: disable=C0301,R0916
                        if (self._prefix_length - max_edit_distance == candidate_len
                                and (min_distance > 1
                                     and phrase[phrase_len + 1 - min_distance :] != suggestion[suggestion_len + 1 - min_distance :])
                                or (min_distance > 0
                                    and phrase[phrase_len - min_distance] != suggestion[suggestion_len - min_distance]
                                    and (phrase[phrase_len - min_distance - 1] != suggestion[suggestion_len - min_distance]
                                         or phrase[phrase_len - min_distance] != suggestion[suggestion_len - min_distance - 1]))):
                            continue
                        else:
                            # delete_in_suggestion_prefix is somewhat
                            # expensive, and only pays off when
                            # verbosity is TOP or CLOSEST
                            if ((verbosity != Verbosity.ALL
                                 and not self._delete_in_suggestion_prefix(candidate, candidate_len, suggestion, suggestion_len))
                                    or suggestion in considered_suggestions):
                                continue
                            considered_suggestions.add(suggestion)
                            distance = distance_comparer.compare(
                                phrase, suggestion, max_edit_distance_2)
                            if distance < 0:
                                continue
                    # do not process higher distances than those
                    # already found, if verbosity<ALL (note:
                    # max_edit_distance_2 will always equal
                    # max_edit_distance when Verbosity.ALL)
                    if distance <= max_edit_distance_2:
                        suggestion_count = self._words[suggestion]
                        si = SuggestItem(suggestion, distance,
                                         suggestion_count)
                        if suggestions:
                            if verbosity == Verbosity.CLOSEST:
                                # we will calculate DamLev distance
                                # only to the smallest found distance
                                # so far
                                if distance < max_edit_distance_2:
                                    suggestions = list()
                            elif verbosity == Verbosity.TOP:
                                if (distance < max_edit_distance_2
                                        or suggestion_count > suggestions[0].count):
                                    max_edit_distance_2 = distance
                                    suggestions[0] = si
                                continue
                        if verbosity != Verbosity.ALL:
                            max_edit_distance_2 = distance
                        suggestions.append(si)
            # add edits: derive edits (deletes) from candidate (phrase)
            # and add them to candidates list. this is a recursive
            # process until the maximum edit distance has been reached
            if (len_diff < max_edit_distance
                    and candidate_len <= self._prefix_length):
                # do not create edits with edit distance smaller than
                # suggestions already found
                if (verbosity != Verbosity.ALL
                        and len_diff >= max_edit_distance_2):
                    continue
                for i in range(candidate_len):
                    delete = candidate[: i] + candidate[i + 1 :]
                    if delete not in considered_deletes:
                        considered_deletes.add(delete)
                        candidates.append(delete)
        if len(suggestions) > 1:
            suggestions.sort()

        early_exit()
        return suggestions

    def _delete_in_suggestion_prefix(self, delete, delete_len, suggestion,
                                     suggestion_len):
        """Check whether all delete chars are present in the suggestion
        prefix in correct order, otherwise this is just a hash
        collision
        """
        if delete_len == 0:
            return True
        if self._prefix_length < suggestion_len:
            suggestion_len = self._prefix_length
        j = 0
        for i in range(delete_len):
            del_char = delete[i]
            while j < suggestion_len and del_char != suggestion[j]:
                j += 1
            if j == suggestion_len:
                return False
        return True

    def _parse_words(self, text):
        """Create a non-unique wordlist from sample text
        language independent (e.g. works with Chinese characters)
        """
        # // \w Alphanumeric characters (including non-latin
        # characters, umlaut characters and digits) plus "_". [^\W_] is
        # the equivalent of \w excluding "_".
        # Compatible with non-latin characters, does not split words at
        # apostrophes.
        # Uses capturing groups to combine a negated set with a
        # character set
        matches = re.findall(r"(([^\W_]|['’])+)", text.lower())
        # The above regex returns ("ghi'jkl", "l") for "ghi'jkl", so we
        # extract the first element
        matches = [match[0] for match in matches]
        return matches

    def _edits(self, word, edit_distance, delete_words):
        """Inexpensive and language independent: only deletes,
        no transposes + replaces + inserts replaces and inserts are
        expensive and language dependent
        """
        edit_distance += 1
        word_len = len(word)
        if word_len > 1:
            for i in range(word_len):
                delete = word[: i] + word[i + 1 :]
                if delete not in delete_words:
                    delete_words.add(delete)
                    # recursion, if maximum edit distance not yet
                    # reached
                    if edit_distance < self._max_dictionary_edit_distance:
                        self._edits(delete, edit_distance, delete_words)
        return delete_words

    def _edits_prefix(self, key):
        hash_set = set()
        if len(key) <= self._max_dictionary_edit_distance:
            hash_set.add("")
        if len(key) > self._prefix_length:
            key = key[: self._prefix_length]
        hash_set.add(key)
        return self._edits(key, 0, hash_set)

    @property
    def bigrams(self):
        return self._bigrams

    @property
    def deletes(self):
        return self._deletes

    @property
    def replaced_words(self):
        return self._replaced_words

    @property
    def words(self):
        return self._words

    @property
    def word_count(self):
        return len(self._words)

class SuggestItem(object):
    def __init__(self, term, distance, count):
        self._term = term
        self._distance = distance
        self._count = count

    def __eq__(self, other):
        if self._distance == other.distance:
            return self._count == other.count
        else:
            return self._distance == other.distance

    def __lt__(self, other):
        if self._distance == other.distance:
            return self._count > other.count
        else:
            return self._distance < other.distance

    def __str__(self):
        return "{}, {}, {}".format(self._term, self._distance, self._count)

    @property
    def term(self):
        return self._term

    @term.setter
    def term(self, term):
        self._term = term

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, distance):
        self._distance = distance

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, count):
        self._count = count

