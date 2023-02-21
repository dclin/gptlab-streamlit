import json 
import time 
from google.cloud import firestore 
import streamlit as st 

db_key_dict = json.loads(st.secrets["firestore"]["db-key"])

class firestore_db:
    def __init__(self):
        self.db = firestore.Client.from_service_account_info(db_key_dict)

    def get_doc(self, collection_name, document_id, field_names=None, return_reference_only=None, max_tries=3, initial_backoff=1):
        doc_ref = self.db.collection(collection_name).document(document_id)
        tries = 0
        backoff = initial_backoff 
        while True:
            try:
                if not doc_ref.get().exists:
                    return None 
                if return_reference_only == True:
                    return doc_ref
                else:
                    doc = {"id": document_id}
                    if not field_names or not isinstance(field_names, (list, tuple)):
                        doc["data"] = doc_ref.get().to_dict()
                    else:
                        doc["data"] = {}
                        for field_name in field_names:
                            if doc_ref.get().get(field_name):
                                doc["data"][field_name] = doc_ref.get().get(field_name)
                    return doc
            except:
                if tries >= max_tries:
                    return None
                time.sleep(backoff)
                backoff *= 2
                tries += 1

    def get_sub_collection_item(self, collection_name, document_id, sub_collection_name, sub_document_id, field_names=None, max_tries=3, initial_backoff=1):
        doc_ref = self.get_doc(collection_name=collection_name, document_id=document_id, return_reference_only=True, max_tries=max_tries, initial_backoff=initial_backoff)

        if not doc_ref.get().exists:
            return None 

        tries = 0
        backoff = initial_backoff 
        while True:
            try:
                sub_doc_ref = doc_ref.collection(sub_collection_name).document(sub_document_id)

                if not sub_doc_ref.get().exists:
                    return None 

                sub_doc = {"id": sub_document_id}

                if not field_names or not isinstance(field_names, (list, tuple)):
                    sub_doc["data"] = sub_doc_ref.get().to_dict()
                else:
                    sub_doc["data"] = {}
                    for field_name in field_names:
                        if sub_doc_ref.get().get(field_name):
                            sub_doc["data"][field_name] = sub_doc_ref.get().get(field_name)
                return sub_doc 
            except:
                if tries >= max_tries:
                    return None
                time.sleep(backoff)
                backoff *= 2
                tries += 1

    # get a list of documents within a collection 
    # query_filters: query_filters = [ ("is_active", "==", True)]
    # field_names: field_names = ['name','is_active']
    # example: 
    def get_docs(
            self, 
            collection_name, 
            query_filters=None, 
            field_names=None, 
            order_by_field=None, 
            order_by_direction='ASCENDING', 
            limit=None, 
            max_tries=3, 
            initial_backoff=1
        ):
        collection_ref = self.db.collection(collection_name)

        docs = collection_ref.limit(1).stream()
        if not list(docs):
            return None 

        query = collection_ref
        if query_filters:
            for query_filter in query_filters:
                query = query.where(query_filter[0], query_filter[1], query_filter[2])

        if order_by_field:
            if order_by_direction == 'ASCENDING':
                query = query.order_by(order_by_field)
            elif order_by_direction == 'DESCENDING':
                query = query.order_by(order_by_field, direction=firestore.Query.DESCENDING)


        if limit:
            query = query.limit(limit)

        docs = []
        tries = 0
        backoff = initial_backoff
        while True:
            try:
                query_results = query.get()
                for doc in query_results:
                    doc_dict = {"id": doc.id}
                    if not field_names or not isinstance(field_names, (list, tuple)):
                        doc_dict["data"] = doc.to_dict()
                    else:
                        doc_dict["data"] = {}
                        for field_name in field_names:
                            if doc.get(field_name):
                                doc_dict["data"][field_name] = doc.get(field_name)
                    docs.append(doc_dict)
                return docs
            except:
                if tries >= max_tries:
                    return None
                time.sleep(backoff)
                backoff *= 2
                tries += 1

    def increment_document_fields(self, collection_name, document_id, field_name, increment=1, max_tries=3, initial_backoff=1):
        doc_ref = self.db.collection(collection_name).document(document_id)

        tries = 0
        backoff = initial_backoff
        while True:
            try:
                doc = doc_ref.get().to_dict()

                if not doc:
                    return None
                current_value = doc.get(field_name)

                if not current_value:
                    doc_ref.set({field_name: increment}, merge=True)
                else:
                    doc_ref.update({field_name: current_value + increment})
                return True
            except:
                if tries >= max_tries:
                    return None
                time.sleep(backoff)
                backoff *= 2
                tries += 1

    # db.update_document_fields("collection_name", "document_id", {"field1": value1, "field2": value2})
    def update_document_fields(self, collection_name, document_id, updates, max_tries=3, initial_backoff=1):
        doc_ref = self.db.collection(collection_name).document(document_id)

        tries = 0
        backoff = initial_backoff
        while True:
            try:
                doc = doc_ref.get().to_dict()

                if not doc:
                    return None

                doc_ref.update(updates)
                return True
            except:
                if tries >= max_tries:
                    return None
                time.sleep(backoff)
                backoff *= 2
                tries += 1


    def create_doc(self, collection_name, data, id=None, max_tries=3, initial_backoff=1):
        collection_ref = self.db.collection(collection_name)

        tries = 0
        backoff = initial_backoff
        while True:
            try:
                doc_ref = None
                if id != None:
                    doc_ref = collection_ref.document(id)
                else:
                    doc_ref = collection_ref.document()
                doc_ref.set(data)
                return doc_ref.id
            except:
                if tries >= max_tries:
                    return None
                time.sleep(backoff)
                backoff *= 2
                tries += 1

    def create_sub_collection_item(self, collection_name, document_id, sub_collection_name, data, max_tries=3, initial_backoff=1):
        doc_ref = self.db.collection(collection_name).document(document_id)

        tries = 0
        backoff = initial_backoff
        while True:
            try:
                if not doc_ref.get().exists:
                    return None
                sub_collection_ref = doc_ref.collection(sub_collection_name)
                item_ref = sub_collection_ref.document()
                item_ref.set(data)
                return item_ref.id
            except:
                if tries >= max_tries:
                    return None
                time.sleep(backoff)
                backoff *= 2
                tries += 1


# Testing 
#if __name__ == '__main__':

    # a = firestore_db()
    # create a doc PASS 
    #a.create_doc(collection_name="bots", data={"test_field":1})

    # create a sub-collection-tiem: PASS 
    #a.create_sub_collection_item(collection_name="bots", document_id="1AHDQXZZPplJ5S4E9zia", sub_collection_name="messages",data={"test_field":1})

    # increment document fields: PASS 
    #a.increment_document_fields(collection_name="bots", document_id="1AHDQXZZPplJ5S4E9zia", field_name="mama_count", increment=-20)

    # passed -- but can't use order by and query filter together -- may need index 
    # query_filters = [("is_active","==",True),("showcased","==",True)]
    # field_names = ['name','is_active']
    #order_by_field
    #bots = a.get_docs(collection_name="bots", query_filters=query_filters, field_names=field_names)
    # bots = a.get_docs(collection_name="bots", order_by_field="name", field_names=field_names)
    # for b in bots:
    #     print(b)

    # test raw queries 
    # db = firestore.Client()
    # bots_ref = db.collection("bots")
    # query = bots_ref.where("showcased","==",True).where("is_active","==",True)
    # results = query.get()

    # for doc in results:
    #     d = doc.to_dict()
    #     print(doc.id, d['name'])

    # field_names = ['name','is_active']
    # print(a.get_doc(collection_name="bots",document_id="dXLAPBmqgnOoucNg0I2D",field_names=field_names))

    # field_names=['config']

    # item = a.get_sub_collection_item(collection_name="bots", document_id="dXLAPBmqgnOoucNg0I2D", sub_collection_name="model_configs", sub_document_id="Z65rdCKJIPLCfmyDReli",field_names=field_names)
    # print(item)