# -*- coding: utf-8 -*-

from pyramid.view import view_config

from searchcashsystemserver.clasissifyintent import SPECIFY, PARALLEL, GENERALIZE
from searchcashsystemserver.models import Query, DBSession, Document, Relation, DocumentRelation


def register_query(json):
    # クエリを登録する
    for k, v in json.items():

        query = DBSession.query(Query).filter(Query.query == k).first()
        if query is None:
            query = Query(k)
        query.count += 1

        DBSession.add(query)
        DBSession.flush()

        documents = v['documents']
        # クリックしたドキュメントを登録
        for doc in documents:
            document = DBSession.query(Document).filter(Document.url == doc['url']).first()
            if document is None:
                document = Document(doc['url'], doc['title'], '')
            DBSession.add(document)
            DBSession.flush()

            d_relation = DBSession.query(DocumentRelation).filter(DocumentRelation.query_id == query.id).filter(
                DocumentRelation.document_id == document.id).first()
            if d_relation is None:
                d_relation = DocumentRelation(query.id, document.id)
            d_relation.click_count += 1
            DBSession.add(d_relation)


def register_queries_relation(first_query, queries, intent):
    for q in queries:
        p_query = DBSession.query(Query).filter(Query.query == first_query).first()
        n_query = DBSession.query(Query).filter(Query.query == q).first()

        relation = DBSession.query(Relation).filter(Relation.first_id == p_query.id).filter(
            Relation.second_id == n_query.id).first()

        if relation is None:
            relation = Relation(p_query.id, n_query.id, intent)

        relation.count += 1
        DBSession.add(relation)


def register_relations(json):
    for k, v in json.items():
        children = v['children']
        friends = v['friends']
        parents = v['parents']

        # どのクエリにも繋がっていないクエリはスルー
        if (len(children) == 0 and len(friends) == 0 and len(parents) == 0):
            continue

        register_queries_relation(k, children, SPECIFY)
        register_queries_relation(k, parents, GENERALIZE)
        register_queries_relation(k, friends, PARALLEL)


@view_config(route_name='registerSearch', renderer='json', request_method='POST')
def register_search_data(request):
    json = request.json_body
    register_query(json)
    register_relations(json)

    return {
        'success_code': 0
    }
