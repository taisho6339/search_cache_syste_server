# -*- coding: utf-8 -*-
from math import log, sqrt

import MeCab


ALL_QUERIES = 31278


def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[
                             j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1  # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def get_same_char_count_from_left(s1, s2):
    length = min(len(s1), len(s2))
    count = 0
    for i in range(length):
        if s1[i] == s2[i]:
            count += 1
    return count


def get_same_char_count_from_right(s1, s2):
    s1 = s1[::-1]
    s2 = s2[::-1]
    length = min(len(s1), len(s2))
    count = 0
    for i in range(length):
        if s1[i] == s2[i]:
            count += 1
    return count


def get_same_word_count_form_left(s1, s2):
    s_s1 = s1.split()
    s_s2 = s2.split()
    length = min(len(s_s1), len(s_s2))
    count = 0
    for i in range(length):
        if s_s1[i] == s_s2[i]:
            count += 1
    return count


def get_same_word_count_from_right(s1, s2):
    s_s1 = s1.split()
    s_s2 = s2.split()
    length = min(len(s_s1), len(s_s2))
    s_s1 = s_s1[::-1]
    s_s2 = s_s2[::-1]
    count = 0
    for i in range(length):
        if s_s1[i] == s_s2[i]:
            count += 1
    return count


def get_same_word_count(s1, s2):
    s_s1 = s1.split()
    s_s2 = s2.split()
    count = 0
    for i in range(len(s_s1)):
        if s_s1[i] in s_s2:
            count += 1
    return count


def jaccard(s1, s2):
    v1 = s1.split()
    v2 = s2.split()
    numerator = sum([c in v2 for c in v1])
    denominator = len(v1) + len(v2) - numerator
    return float(numerator) / denominator if denominator != 0 else 0


def extract_word_from_snippets(snipetts):
    mecab = MeCab.Tagger('-Ochasen')
    mecab.parse(snipetts[0])
    word_list = []
    for i in range(len(snipetts)):
        node = mecab.parseToNode(snipetts[i])
        while node.next:
            posid = node.posid
            if (posid >= 38 and posid <= 60):
                if (48 <= posid and posid <= 50):
                    node = node.next
                    continue
                if (posid == 53):
                    node = node.next
                    continue
                word_list.append(node.surface)
            node = node.next
    return word_list


def create_vector_word_entries(snipetts1, snipetts2):
    list1 = [snipetts1[i] for i in range(len(snipetts1))]
    list2 = [snipetts2[i] for i in range(len(snipetts2))]
    list1.extend(list2)
    output = []
    for i in range(len(list1)):
        if list1[i] in output:
            continue
        output.append(list1[i])
    return output


def retrieve_appearance_count(word, snipetts):
    count = 0
    for i in range(len(snipetts)):
        if word in snipetts[i]:
            count += 1
    return count


def calc_cosine_similarity(vector1, vector2):
    vector_size1 = 0
    vector_size2 = 0
    inner_product = 0
    for i in range(len(vector1)):
        vector_size1 += vector1[i] ** 2
        vector_size2 += vector2[i] ** 2
        inner_product += vector1[i] * vector2[i]
    sum_vector_size_sqrt = (sqrt(vector_size1) * sqrt(vector_size2))
    if sum_vector_size_sqrt == 0:
        return 0
    similarity = inner_product / sum_vector_size_sqrt
    return similarity


def get_snippet_vectors(s_list1, s_list2, cursor):
    # 各スニペットの単語を収集しておく
    # 構成要素を確定する 1と2で出てくる名詞単語すべて

    snipetts1_words = extract_word_from_snippets(s_list1)  # query1のスニペットに出てくる単語すべて
    snipetts2_words = extract_word_from_snippets(s_list2)  # query2のスニペットに出てくる単語すべて
    word_entries = create_vector_word_entries(snipetts1_words, snipetts2_words)

    # sql = '''select count(q) from queries where q like '%s' '''
    vector1 = []
    vector2 = []
    for k in word_entries:
        tf_1 = retrieve_appearance_count(k, s_list1)
        tf_2 = retrieve_appearance_count(k, s_list2)

        # cursor.execute(sql % ("%" + k + "%"))
        # count = cursor.fetchone()[0]
        # idf = log(ALL_QUERIES)
        # if count > 0:
        # idf -= log(count)
        idf = 1
        vector1.append(tf_1 * idf)
        vector2.append(tf_2 * idf)

    return [vector1, vector2]


def get_word_add(query1, query2):
    common_word_count = get_same_word_count(query1, query2)
    if common_word_count == 0:
        return 0
    query_words1 = query1.split()
    query_words2 = query2.split()
    return len(query_words2) - len(query_words1)


def get_char_add(query1, query2):
    common_word_count = get_same_word_count(query1, query2)
    if common_word_count == 0:
        return 0
    return len(query2) - len(query1)


# SkewDivergenceの後続スニペットベクトルをスムージング
def calc_smooth_vector(vector1, vector2, alpha=0.3):
    a = 1.0 - alpha
    vector = [(vector2[i] * alpha) + (vector1[i] * a) for i in range(len(vector1))]
    return vector


def calc_skew_divergence(vector1, vector2):
    v_sum = 0
    for i in range(len(vector1)):
        log_v = 0
        if vector1[i] > 0:
            log_v = log(vector1[i])
        if vector2[i] > 0:
            log_v -= log(vector2[i])

        v_sum += vector1[i] * log_v
    return v_sum


def get_svm_params(pre_query, next_query, pre_query_snippets, next_query_snippets):
    # conn = sqlite3.connect('/Users/taisho6339/Dropbox/development_2014_11_08.sqlite3')
    # c = conn.cursor()

    lev = levenshtein(pre_query, next_query)
    c_count_left = get_same_char_count_from_left(pre_query, next_query)
    c_count_right = get_same_char_count_from_right(pre_query, next_query)
    w_count_left = get_same_word_count_form_left(pre_query, next_query)
    w_count_right = get_same_word_count_from_right(pre_query, next_query)
    common_word_count = get_same_word_count(pre_query, next_query)
    jac = jaccard(pre_query, next_query)

    vectors = get_snippet_vectors(pre_query_snippets, next_query_snippets, None)
    cosine_simirality = calc_cosine_similarity(vectors[0], vectors[1])
    word_add = get_word_add(pre_query, next_query)
    char_add = get_char_add(pre_query, next_query)

    s_vector = calc_smooth_vector(vectors[0], vectors[1])
    skew1 = calc_skew_divergence(vectors[0], s_vector)
    s_vector = calc_smooth_vector(vectors[1], vectors[0])
    skew2 = calc_skew_divergence(vectors[1], s_vector)

    return {
        'levenshtein': lev,
        'charcount_left': c_count_left,
        'charcount_right': c_count_right,
        'wordcount_left': w_count_left,
        'wordcount_right': w_count_right,
        'common_word_count': common_word_count,
        'jaccard': jac,
        'cosine_simirality': cosine_simirality,
        'word_add': word_add,
        'char_add': char_add,
        'skew1': skew1,
        'skew2': skew2
    }
