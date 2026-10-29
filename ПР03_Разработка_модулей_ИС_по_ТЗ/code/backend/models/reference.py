from backend.models.base_model import BaseModel


class Room(BaseModel):
    table = 'room'


class PaymentMethod(BaseModel):
    table = 'payment_method'


class Status(BaseModel):
    table = 'status'

    NEW = 1
    ASSIGNED = 2
    DONE = 3
