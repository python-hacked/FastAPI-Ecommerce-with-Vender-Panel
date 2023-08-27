from typing import Optional, List
from pydantic import BaseModel,EmailStr
from datetime import date
import uuid



class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class createuser(BaseModel):
    name : str
    email : EmailStr
    phone :str
    password : str

class loginuser(BaseModel):
    email : str
    password : str

class updateuser(BaseModel):
    id : int
    name : str
    email : str
    password :str
    phone :int

class deleteuser(BaseModel):
    user_email : str

class category(BaseModel):
    name : str
    

class updatecategory(BaseModel):
    id : int
    name : str

class deletecategory(BaseModel):
    id : int

class subcategory(BaseModel):
    name : str

class updatesubcategory(BaseModel):
    id : int
    name : str

class deletesubcategory(BaseModel):
    id : int


class product_add(BaseModel):
    name : str
    price : int
    discountprice: int
    category_id : int
    description : str
    subcategory_id :int

class product_view(BaseModel):
    id :int

class updateproduct(BaseModel):
    id : int
    name : str
    price : int
    category_id : int
    description : str
    subcategory_id :int


class deleteproduct(BaseModel):
    id : int
 
class productview(BaseModel) :
    id : int

class profiledt(BaseModel) :
    address : str
    city : str
    zipcode : int
    state : str

class cartItems(BaseModel):
    product_id:str 
    quantity: int 
    flag: str

class deletecartproduct(BaseModel):
    id : int

class orderstatus(BaseModel):
    name : str