from __future__ import annotations
# ...existing code...
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
try:
    from bson import ObjectId as _ObjectId  # type: ignore
except Exception:  # fallback for environments without bson
    _ObjectId = None  # type: ignore


class MongoBaseModel(BaseModel):
    """
    Base model that:
      - maps Mongo `_id` <-> model `id`
      - ignores unknown fields (so `_id` can be dropped if never needed)
      - provides from_mongo / to_mongo helpers
    """

    id: Optional[str] = Field(None, alias="_id")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"
        # if bson.ObjectId is available, encode it as str in JSON
        json_encoders = {}
        if _ObjectId is not None:
            json_encoders[_ObjectId] = lambda v: str(v)

    @classmethod
    def from_mongo(cls, doc: Optional[Dict[str, Any]]):
        """
        Normalize a raw MongoDB document and create a Pydantic model.
        Converts ObjectId -> str for `_id`. Ignores other unknown fields.
        """
        if doc is None:
            return None
        normalized = dict(doc)  # shallow copy
        if "_id" in normalized:
            try:
                # convert ObjectId to str if possible
                normalized["_id"] = str(normalized["_id"])
            except Exception:
                pass
        return cls.parse_obj(normalized)

    def to_mongo(self, include_id: bool = False) -> Dict[str, Any]:
        """
        Produce a dict suitable for MongoDB operations.
        - by_alias=True emits `_id` (alias) instead of `id` when present.
        - include_id: if False the `_id` key will be removed before returns.
        - attempts to convert `_id` string back to ObjectId when bson is available.
        """
        doc = self.dict(by_alias=True, exclude_none=True)
        if not include_id and "_id" in doc:
            doc.pop("_id")
            return doc
        if "_id" in doc and _ObjectId is not None:
            try:
                doc["_id"] = _ObjectId(doc["_id"])
            except Exception:
                # leave as-is (string) if conversion fails
                pass
        return doc




# Example Model + repositoy usages : 
# ...existing code...
from typing import Optional
from .mongo_pydantic import MongoBaseModel

class PaymentCenter(MongoBaseModel):
    payment_center_id: int
    vendor_name: Optional[str]
    tax_id: Optional[str]
    npi: Optional[str]



# ...existing code...
# pseudocode showing conversion patterns
def get_payment_centers(collection, filter):
    # collection = pymongo.Collection
    docs = collection.find(filter)
    return [PaymentCenter.from_mongo(doc) for doc in docs]


def insert_payment_center(collection, model: PaymentCenter):
    doc = model.to_mongo(include_id=False)
    res = collection.insert_one(doc)
    # if you want to return model with `_id` populated:
    inserted = collection.find_one({"_id": res.inserted_id})
    return PaymentCenter.from_mongo(inserted)




# Key notes

# To accept _id from DB but never expose it, keep Config.extra="ignore" and do not rely on the id field; use from_mongo to drop/convert it.
# To accept and later write _id back, keep id: Optional[str] = Field(None, alias="_id"), use dict(by_alias=True) / to_mongo(include_id=True) and convert to ObjectId when writing.
# Use from_mongo for all DB reads and to_mongo() for writes so conversion is centralized.
# For nested/dynamic schemas the same approach applies: nested models will be parsed automatically if the field types are Pydantic models.
# Validate performance: when reading many docs, stream and parse in batches to avoid memory spikes (see process_flow.md for batching guidance).
# If you want, I can add a small utilities file with an ObjectId wrapper and an example repository file wired to PyMongo in this workspace.