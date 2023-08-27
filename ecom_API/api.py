from fastapi import FastAPI, File, UploadFile,Depends
from fastapi import APIRouter
from ecom_API.pydantic_models import *
from . models import *


from fastapi.responses import JSONResponse
from fastapi_login import LoginManager
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, Request,Form
from pathlib import Path
import secrets
from fastapi.staticfiles import StaticFiles
from PIL import Image

from datetime import datetime, timedelta
from slugify import slugify


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent


templates = Jinja2Templates(directory=str (Path(BASE_DIR,"ecom_API/templates")))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET = 'your-secret-key'
manager = LoginManager(SECRET, token_url='/auth/token')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)




@router.post("/registration/")
async def readeuser(data: createuser):
    if await Create_user.filter(email=data.email).exists():
        return {"status": True,
                "message": "email already exists"}
    else:
        api_obj = await Create_user.create(name=data.name, email=data.email,
                                           phone=data.phone, password=get_password_hash(data.password))

    return api_obj


@manager.user_loader()
async def load_user(email: str):
    if await Create_user.exists(email=email):
        newapi1 = await Create_user.get(email=email)
        return newapi1




@router.post('/login/', )
async def login(data: loginuser):

    email = data.email
    user = await load_user(email)

    if not user:
        return JSONResponse({'status': False, 'message': 'User not Registered'}, status_code=403)
    elif not verify_password(data.password, user.password):
        return JSONResponse({'status': False, 'message': 'Invalid password'}, status_code=403)
    access_token = manager.create_access_token(
        data={'sub': jsonable_encoder(
            user.email), "name": jsonable_encoder(user.email)}

    )
    '''test  current user'''

    new_dict = jsonable_encoder(user)
    new_dict.update({"access_token": access_token})
    return Token(access_token=access_token, token_type='bearer')

@router.put("/update/")
async def update_user(data:updateuser):
        if await Create_user.exists(id =data.id):
                user_obj = await Create_user.filter(id = data.id).update(name = data.name,email= data.email,password=data.password,phone = data.phone)
                print(user_obj)
                return {"Update user"}

@router.delete("/delete/")
async def delete_user(data: deleteuser):
    delete_user = await Create_user.filter(email=data.user_email).delete()
    return  {"user delete successfully"}


@router.get('/alluser/')
async def read_user():
    alluser = await Create_user.all()
    return alluser  

@router.post("/Category/")
async def create_category(data: category):
    if await Category.filter(name=data.name).exists():
        return {"message": "category already exists"}
    else:
        category_obj = await Category.create(name=data.name, slug=slugify(data.name))

        return {"message": " Category added"}

@router.put("/update_category/")
async def update_categorys(data:updatecategory):
        if await Category.exists(id =data.id):
                category_obj = await Category.filter(id = data.id).update(name = data.name)
                print(category_obj)
                return {"Update category"}


@router.delete("/delete_category/")
async def delete_category(data: deletecategory):
    delete_user = await Category.filter(id=data.id).delete()
    return  {"Category delete successfully"}


@router.get('/all_Category/')
async def read_category():
    alluser = await Category.all()
    return alluser 

@router.post("/Subcategory/")
async def create_subcategory(data: subcategory, category_id: int):
    category = await Category.get(id=category_id,)
    

    if await SubCategory.filter(name=data.name).exists():
        return {"message": "category already exists"}
    else:
        subcategory_obj = await SubCategory.create(name=data.name, slug=slugify(data.name), category_id=category_id)

        return {"message": " Subcategory added"}

@router.put("/update_subcategory/")
async def update_subcategorys(data:updatesubcategory):
        if await SubCategory.exists(id =data.id):
                subcategory_obj = await SubCategory.filter(id = data.id).update(name = data.name)
                print(subcategory_obj)
                return {"Update subcategory"}


@router.delete("/delete_subcategory/")
async def delete_subcategory(data: deletesubcategory):
    delete_user = await SubCategory.filter(id=data.id).delete()
    return  {"Subcategory delete successfully"}


@router.get('/all_Subcategory/')
async def read_subcategory():
    alluser = await SubCategory.all()
    return alluser 

@router.post('/product_img/')
async def create_upload(file:UploadFile):

     FILEPATH="static/product"
     filename= file.filename
     extention= filename.split(".")[1]

     if extention not in ["png","jpg"]:
       return{"status":"error","detail":"File extention not allow"}

     else:
            token_name = secrets.token_hex(10)+"."+extention
            generated_name = FILEPATH + token_name
            file_content = await file.read()

            with open(generated_name, "wb") as file:
                        file.write(file_content)

            img = Image.open(generated_name)
            img = img.resize(size =(500,500))
            img.save(generated_name)

            file.close()

            a = await Photo.create(product_image=generated_name)
                
            return {"photo added"}


@router.post('/add_product/')
async def create_product(data: product_add=Depends(),file:UploadFile=File(...),_=Depends()):

     FILEPATH="static/product"
     filename= file.filename
     extention= filename.split(".")[1]

     if extention not in ["png","jpg","jpeg"]:
       return{"status":"error","detail":"File extention not allow"}

     else:
            token_name = secrets.token_hex(10)+"."+extention
            generated_name = FILEPATH + token_name
            file_content = await file.read()
            print("yes")
            with open(generated_name, "wb") as file:
                        file.write(file_content)

            img = Image.open(generated_name)
            img = img.resize(size =(300,250))
            img.save(generated_name)

            file.close()

            a = await Add_products.create(product_image=generated_name,
                                          name=data.name,
                                          price=data.price,
                                            description=data.description,
                                            category_id=data.category_id,
                                            subcategory_id=data.subcategory_id,
                                            slug=slugify(data.name),
                                            discountprice=data.discountprice)
            return a



@router.get('/all_product/')
async def read_products():
    allproduct = await Add_products.all()
    return allproduct

@router.put("/update_product/")
async def update_product(data:updateproduct=Depends(),file:UploadFile=File(...),_=Depends()):

    FILEPATH="static/product"
    filename= file.filename
    extention= filename.split(".")[1]

    if extention not in ["png","jpg"]:
       return{"status":"error","detail":"File extention not allow"}

    else:
            token_name = secrets.token_hex(10)+"."+extention
            generated_name = FILEPATH + token_name
            file_content = await file.read()
            print("yes")
            with open(generated_name, "wb") as file:
                        file.write(file_content)

            img = Image.open(generated_name)
            img = img.resize(size =(500,500))
            img.save(generated_name)

            file.close()
    
    
            if await Add_products.exists(id =data.id):
                product_obj = await Add_products.filter(id = data.id).update(name=data.name,
                                          price=data.price,
                                            description=data.description,
                                            category_id=data.category_id,
                                            subcategory_id=data.subcategory_id,
                                            slug=slugify(data.name),
                                            product_image=generated_name,)
                return {"Update product"}


@router.delete("/delete_product/")
async def delete_producty(data: deleteproduct):
    delete_products = await Add_products.filter(id=data.id).delete()
    return  {"Product delete successfully"}

@router.delete("/delete_cartproduct/")
async def delete_cartproducty(data: deletecartproduct):
    delete_products = await ADDincart.filter(id=data.id).delete()
    return  {"Product delete successfully"}



@router.get('/view_productss/')
async def read_productss(id:str):
    product = await Add_products.filter(id=id)
    return product

@router.get("/profile/")
async def read_item(request: Request,email:EmailStr):  

    if await Create_user.exists(email= email):
        user_obj= await Create_user.get(email=email)
    else:
        user_obj = None
   
    
    return JSONResponse({
                   "status": True, "message": jsonable_encoder(update_profile)
                    })



@router.post("/status/")
async def create_status(data: orderstatus):
    status = await Orderstatus.create(name=data.name, slug=slugify(data.name))

    return {"message": " status added"}