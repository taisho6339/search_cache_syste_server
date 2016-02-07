# -*- coding: utf-8 -*-

from pyramid.view import view_config
from sqlalchemy.sql.expression import desc

from searchcashsystemserver.models import Query, DBSession, Document, Relation, DocumentRelation


def retrieve_query_relations(search_query, intent):
    sql_query = DBSession.query(Relation).filter(Relation.first_id == search_query.id)
    sql_query = sql_query.filter(Relation.intent == intent)
    relations = sql_query.order_by(desc(Relation.count)).all()

    return relations


def retrieve_document_by_intent(search_query, intent):
    relations = retrieve_query_relations(search_query, intent)
    recommends = {}
    document_count = 0
    for relation in relations:

        if document_count > 10:
            break

        transit_query = DBSession.query(Query).filter(Query.id == relation.second_id).first()
        # 1クエリにつき上位３件だけ取得
        d_relations = DBSession.query(DocumentRelation).filter(DocumentRelation.query_id == transit_query.id).order_by(
            desc(DocumentRelation.click_count)).limit(3).all()
        for d_relation in d_relations:
            document = DBSession.query(Document).filter(Document.id == d_relation.document_id).first()
            data = {
                'title': document.title,
                'url': document.url,
            }
            recommends.setdefault(transit_query.query, [])
            recommends[transit_query.query].append(data)
            document_count += 1

    return recommends


@view_config(route_name='retrieveRecommend', renderer='json', request_method='GET')
def retrieve_recommend_data(request):
    query = request.GET.get('query', '')
    intent = request.GET.get('intent', '')

    # 0が絞込、1が汎化、2が関連
    search_query = DBSession.query(Query).filter(Query.query == query).first()
    if search_query is None:
        return [{}, {}, {}]

    if intent != '':
        recommend = [
            retrieve_document_by_intent(search_query, intent)
        ]
    else:
        recommend = [
            retrieve_document_by_intent(search_query, Relation.SPECIFY),
            retrieve_document_by_intent(search_query, Relation.GENERALIZE),
            retrieve_document_by_intent(search_query, Relation.PARALLEL)
        ]

    return {
        'recommends': recommend
    }