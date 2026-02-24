import implicit
from scipy.sparse import csr_matrix
from models import MongoDBEnum
from sklearn.preprocessing import LabelEncoder
from models import BaseDataModel


class ALSModel(BaseDataModel):

    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[MongoDBEnum.COLLECTION_EVENT_NAME.value]


    
    async def get_user_item_score_matrix(self):
        pipeline = [
                {"$unwind": "$event"},
                {
                    "$group": {
                        "_id": {
                            "user_id": "$event.user_id",
                            "product_link": "$event.product_link"
                        },
                        "total_score": {"$sum": "$event.score"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "user_id": "$_id.user_id",
                        "product_link": "$_id.product_link",
                        "total_score": 1
                    }
                }
            ]

        cursor = self.collection.aggregate(pipeline)

        records = []
        async for doc in cursor:
            records.append(doc)

        return records
    
    def build_sparse_matrix(self, records):
        user_ids = [r["user_id"] for r in records]
        product_links = [r["product_link"] for r in records]
        scores = [r["total_score"] for r in records]

        self.user_encoder = LabelEncoder()
        self.item_encoder = LabelEncoder()

        user_indices = self.user_encoder.fit_transform(user_ids)
        item_indices = self.item_encoder.fit_transform(product_links)

        sparse_matrix = csr_matrix(
            (scores, (user_indices, item_indices))
        )

        return sparse_matrix
    

    def train(self, sparse_matrix):
        self.model = implicit.als.AlternatingLeastSquares(
            factors=50,
            iterations=20,
            regularization=0.1
        )
        # implicit expects item-user matrix
        self.model.fit(sparse_matrix.T)


    def recommend(self, user_id, sparse_matrix, n=10):
        if user_id not in self.user_encoder.classes_:
            return []  # cold start — user unseen

        user_index = self.user_encoder.transform([user_id])[0]

        recommended_ids, scores = self.model.recommend(
            user_index,
            sparse_matrix[user_index],
            N=n,
            filter_already_liked_items=True
        )

        recommended_products = self.item_encoder.inverse_transform(recommended_ids)
        return [
            {"product_link": p, "score": float(s)}
            for p, s in zip(recommended_products, scores)
            if s > .5
        ]