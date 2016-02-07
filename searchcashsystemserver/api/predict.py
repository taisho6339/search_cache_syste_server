# -*- coding: utf-8 -*-

from pyramid.view import view_config

from searchcashsystemserver.clasissifyintent import get_intent, get_classify_str


@view_config(route_name='intent', renderer='json', request_method='GET')
def predict_search_intent(request):
    p_query = request.GET.get('pre_query', '')
    n_query = request.GET.get('next_query', '')
    predict = get_intent(p_query, n_query)
    return {
        'intent_type': str(predict),
        'intent_str': get_classify_str(predict)
    }