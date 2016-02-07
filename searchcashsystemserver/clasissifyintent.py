# -*- coding: utf-8 -*-
from searchcashsystemserver.models import CLF
from searchcashsystemserver.searchquery import retrieve_snippet
from searchcashsystemserver.svmparams import get_svm_params

SPECIFY = 0
GENERALIZE = 1
PARALLEL = 2
FORMAT = 3
NEW = 4


def get_classify_str(classify):
    if classify == SPECIFY:
        return '絞込'

    elif classify == GENERALIZE:
        return '汎化'

    elif classify == PARALLEL:
        return '関連'

    elif classify == FORMAT:
        return '語句修正'

    else:
        return '新規'


def get_intent(pre_query, next_query):
    p_snippets = retrieve_snippet(pre_query)
    n_snippets = retrieve_snippet(next_query)

    params = get_svm_params(pre_query, next_query, p_snippets, n_snippets)

    test_x = []
    test_x.append(int(params['levenshtein']))
    test_x.append(int(params['charcount_left']))
    test_x.append(int(params['charcount_right']))
    test_x.append(int(params['wordcount_left']))
    test_x.append(int(params['wordcount_right']))
    test_x.append(int(params['common_word_count']))
    test_x.append(float(params['jaccard']))
    test_x.append(float(params['cosine_simirality']))
    test_x.append(int(params['word_add']))
    test_x.append(int(params['char_add']))
    test_x.append(float(params['skew1']) / float(params['skew1']))
    test_x.append(float(params['skew2'] / float(params['skew1'])))

    predict = CLF.predict([test_x])
    return predict[0]

