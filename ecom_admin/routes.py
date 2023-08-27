from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi_login import LoginManager
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends
from fastapi import APIRouter
from . models import *
from ecom_API.models import *
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from fastapi_login.exceptions import InvalidCredentialsException
from starlette.middleware.sessions import SessionMiddleware
import typing
import re
from slugify import slugify
from datetime import datetime, timedelta
from fastapi.security import HTTPBasic, HTTPBasicCredentials


router = APIRouter()
security = HTTPBasic()


def flash(request: Request, message: typing.Any, category: str = "") -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append(
        {"message": message, "category": category})


def get_flashed_messages(request: Request):
    print(request.session)
    return request.session.pop("_messages") if "_messages" in request.session else []


BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory="ecom_admin/templates")
templates.env.globals['get_flashed_messages'] = get_flashed_messages
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET = 'your-secret-key'
manager = LoginManager(SECRET, token_url='/auth/token')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@router.get("/adminregistrationpage/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("adminregistration.html", {"request": request, })


@router.post('/adminregistrationpage/',)
async def create_user(request: Request, admin_image: UploadFile = File(...),
                      email: EmailStr = Form(...),
                      name: str = Form(...),
                      phone: str = Form(...),
                      password: str = Form(...),
                      address: str = Form(...)):
    reg_pass = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat_pass = re.compile(reg_pass)
    mat_pass = re.search(pat_pass, password)

    reg_name = re.compile('^[A-Za-z]+$')
    mat_name = re.search(reg_name, name)

    if await Register_admin.filter(email=email).exists():
        flash(request, "Email already exists", "danger")
        return RedirectResponse("/adminregistrationpage/", status_code=status.HTTP_302_FOUND)
    elif await Register_admin.filter(phone=phone).exists():
        flash(request, "Phone number already exists", "danger")
        return RedirectResponse("/adminregistrationpage/", status_code=status.HTTP_302_FOUND)
    else:
        if not mat_name:
            flash(request, "Your name can be in latters only ", "danger")
            return RedirectResponse("/adminregistrationpage/", status_code=status.HTTP_302_FOUND)
        elif len(phone) != 10:
            flash(request, "Please enter 10 digit number", "danger")
            return RedirectResponse("/adminregistrationpage/", status_code=status.HTTP_302_FOUND)
        elif not mat_pass:
            flash(request, "Your password lenth must be in 6 to 20 and must contain atleast one uppercase, one lower case, one special character, one number ", "danger")
            return RedirectResponse("/adminregistrationpage/", status_code=status.HTTP_302_FOUND)
        else:

            FILEPATH = "static/product"
            filename = admin_image.filename
            extension = filename.split(".")[1]
            imagename = filename.split(".")[0]
            if extension not in ["png", "jpg", "jpeg"]:
                return {"status": "error", "detial": "File extension not allowed"}
            dt = datetime.now()
            dt_timestamp = round(datetime.timestamp(dt))
            modified_image_name = imagename+"_"+str(dt_timestamp)+"."+extension
            genrated_name2 = FILEPATH + modified_image_name
            file_content = await admin_image.read()
            with open(genrated_name2, "wb") as file:
                file.write(file_content)
            file.close()

            user_obj = await Register_admin.create(email=email, name=name, address=address, admin_image=genrated_name2,
                                                   phone=phone, password=get_password_hash(password))
            print(user_obj)
            flash(request, "Registration successfully", "success")
            return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)


@manager.user_loader()
async def load_user(email: str):
    if await Register_admin.exists(email=email):
        newapi1 = await Register_admin.get(email=email)
        return newapi1


@router.get("/adminlogin/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("adminlogin.html", {"request": request, })


@router.post('/adminlogin/', )
async def login(request: Request, email: str = Form(...),
                password: str = Form(...)):

    email = email
    user = await load_user(email)

    if not Register_admin:
        flash(request, "User not exsist", "danger")
        return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)
    elif not verify_password(password, user.password):
        flash(request, "Failed to login", "danger")
        return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)
    else:
        request.session["user_id"] = user.id
        request.session["user_name"] = user.name
        request.session["user_phone"] = user.phone
        request.session["user_email"] = user.email
        request.session["user_address"] = user.address
        request.session["user_admin_image"] = user.admin_image

        print(request.session["user_id"])

        print(request.session["user_name"])
        flash(request, "Login successfully", "success")
        return RedirectResponse("/adminindex/", status_code=status.HTTP_302_FOUND)


@router.get("/editprofile/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: int):
    if "user_id" not in request.session:
        flash(request, "Login required", "danger")
        return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)
    else:
        user = await Register_admin.all()

        return templates.TemplateResponse("editprofile.html", {"request": request, "id": id, "user": user})


@router.post('/update_admin/',)
async def update_admin(request: Request, id: int = Form(...), admin_image: UploadFile = File(...),
                       email: EmailStr = Form(...),
                       name: str = Form(...),
                       phone: str = Form(...),
                       password: str = Form(...),
                       address: str = Form(...)):
    user = await Register_admin.get(id=id)
    reg_pass = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat_pass = re.compile(reg_pass)
    mat_pass = re.search(pat_pass, password)

    reg_name = re.compile('^[A-Za-z]+$')
    mat_name = re.search(reg_name, name)

    if not mat_name:
        flash(request, "Your name can be in latters only ", "danger")
        return templates.TemplateResponse("editprofile.html", {"request": request, "id": id})

    elif len(phone) != 10:
        flash(request, "Please enter 10 digit number", "danger")
        return templates.TemplateResponse("editprofile.html", {"request": request, "id": id})

    elif not mat_pass:
        flash(request, "Your password lenth must be in 6 to 20 and must contain atleast one uppercase, one lower case, one special character, one number ", "danger")
        return templates.TemplateResponse("editprofile.html", {"request": request, "id": id})

    else:

        FILEPATH = "static/product"
        filename = admin_image.filename
        extension = filename.split(".")[1]
        imagename = filename.split(".")[0]
        if extension not in ["png", "jpg", "jpeg"]:
            return {"status": "error", "detial": "File extension not allowed"}
        dt = datetime.now()
        dt_timestamp = round(datetime.timestamp(dt))
        modified_image_name = imagename+"_"+str(dt_timestamp)+"."+extension
        genrated_name2 = FILEPATH + modified_image_name
        file_content = await admin_image.read()
        with open(genrated_name2, "wb") as file:
            file.write(file_content)
        file.close()

        update_product = await Register_admin.filter(id=id).update(email=email, name=name, address=address, admin_image=genrated_name2,
                                                                   phone=phone, password=get_password_hash(password))
        # flash(request, "Registration successfully", "success")
        return RedirectResponse("/adminprofile/", status_code=status.HTTP_302_FOUND)


@router.get('/adminlogout/', )
async def logout(request: Request,):

    request.session.clear()
    return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)


@router.get("/adminindex/", response_class=HTMLResponse)
async def read_item(request: Request,):
    if "user_id" not in request.session:
        flash(request, "Login required", "danger")
        return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)
    else:
        user = await Register_admin.all()
        order_status = await Orderstatus.all()

        orders = await Orderhitory.all().select_related("orderuser", "addressuser", "ostatus")
        totalorder = await Orderhitory.all().count()
        totalproducts = await Add_products.all().count()
        return templates.TemplateResponse("index.html", {"request": request, "orders": orders, "totalorder": totalorder, "totalproducts": totalproducts, "user": user, "order_status": order_status})


@router.get("/adminprofile/", response_class=HTMLResponse)
async def read_item(request: Request):
    if "user_id" not in request.session:
        flash(request, "Login required", "danger")
        return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)
    else:
        user = await Register_admin.all()
        return templates.TemplateResponse("adminprofile.html", {"request": request, "user": user})


@router.get("/adminregistrations/", response_class=HTMLResponse)
async def read_item(request: Request):
    if "user_id" not in request.session:
        flash(request, "Login required", "danger")
        return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)
    else:
        user = await Register_admin.all()

        addu = await Create_user.all()
        return templates.TemplateResponse("registrations.html", {"request": request, "addu": addu, "user": user})


@router.get("/adminorders/", response_class=HTMLResponse)
async def read_item(request: Request):
    if "user_id" not in request.session:
        flash(request, "Login required", "danger")
        return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)
    else:

        order_status = await Orderstatus.all()
        user = await Register_admin.all()
        orders = await Orderhitory.all().select_related("orderuser", "addressuser",)
        return templates.TemplateResponse("orders.html", {"request": request, "orders": orders, "user": user, "order_status": order_status})


@router.post("/update_status/{id}")
async def update_categorys(request: Request, id: int, ostatus_id: int = Form(...),):
    category_obj = await Orderhitory.filter(id=id).update(ostatus_id=ostatus_id)
    return RedirectResponse("/adminindex/", status_code=status.HTTP_302_FOUND)


@router.get("/adminAllproducts/", response_class=HTMLResponse)
async def read_item(request: Request):
    if "user_id" not in request.session:
        flash(request, "Login required", "danger")
        return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)
    else:
        allp = await Add_products.all()
        user = await Register_admin.all()

        return templates.TemplateResponse("products.html", {"request": request, "allp": allp, "user": user})


@router.get("/admincategory/", response_class=HTMLResponse)
async def read_item(request: Request):
    if "user_id" not in request.session:
        flash(request, "Login required", "danger")
        return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)
    else:
        user = await Register_admin.all()
        return templates.TemplateResponse("admincategory.html", {"request": request, "user": user})


@router.post("/Category_admin/")
async def create_category(request: Request, name: str = Form(...),):
    if await Category.filter(name=name).exists():
        return RedirectResponse("/Category_admin/", status_code=status.HTTP_302_FOUND)
    else:
        category_obj = await Category.create(name=name, slug=slugify(name))

        return RedirectResponse("/adminSubCategory/", status_code=status.HTTP_302_FOUND)


@router.get("/adminSubCategory/", response_class=HTMLResponse)
async def read_item(request: Request):
    if "user_id" not in request.session:
        flash(request, "Login required", "danger")
        return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)
    else:
        user = await Register_admin.all()
        cat = await Category.all()
        return templates.TemplateResponse("adminSubCategory.html", {"request": request, "cat": cat, "user": user})


@router.post("/adminSubCategory/")
async def create_subcategory(request: Request, name: str = Form(...), category_id: int = Form(...),
                             ):
    ct = await Category.get(id=category_id)

    if await SubCategory.filter(name=name).exists():
        return RedirectResponse("/adminSubCategory/", status_code=status.HTTP_302_FOUND)
    else:

        await SubCategory.create(name=name, slug=slugify(name), category_id=category_id)
        return RedirectResponse("/adminAddproducts/", status_code=status.HTTP_302_FOUND,)


@router.get("/adminAddproducts/", response_class=HTMLResponse)
async def read_item(request: Request):
    if "user_id" not in request.session:
        flash(request, "Login required", "danger")
        return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)
    else:
        user = await Register_admin.all()
        cat = await Category.all()
        subcat = await SubCategory.all()
        return templates.TemplateResponse("addproducts.html", {"request": request, "cat": cat, "subcat": subcat, "user": user})


@router.post('/adminAddproducts/')
async def create_product(request: Request, product_image: UploadFile = File(...), name: str = Form(...),
                         price: int = Form(...), description: str = Form(...),
                         category_id: int = Form(...), subcategory_id: int = Form(...),
                         discountprice: int = Form(...),):
    FILEPATH = "static/product"
    filename = product_image.filename
    extension = filename.split(".")[1]
    imagename = filename.split(".")[0]
    if extension not in ["png", "jpg", "jpeg"]:
        return {"status": "error", "detial": "File extension not allowed"}
    dt = datetime.now()
    dt_timestamp = round(datetime.timestamp(dt))
    modified_image_name = imagename+"_"+str(dt_timestamp)+"."+extension
    genrated_name = FILEPATH + modified_image_name
    file_content = await product_image.read()
    with open(genrated_name, "wb") as file:
        file.write(file_content)
    file.close()

    await Add_products.create(product_image=genrated_name,
                              name=name,
                              price=price,
                              description=description,
                              category_id=category_id,
                              subcategory_id=subcategory_id,
                              slug=slugify(name),
                              discountprice=discountprice)

    return RedirectResponse("/adminAllproducts/", status_code=status.HTTP_302_FOUND)


@router.get("/editproduct/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: int):
    if "user_id" not in request.session:
        flash(request, "Login required", "danger")
        return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)
    else:
        user = await Register_admin.all()
        cat = await Category.all()
        subcat = await SubCategory.all()

        return templates.TemplateResponse("editproduct.html", {"request": request, "cat": cat, "subcat": subcat, "id": id, "user": user})


@router.post("/update_product/")
async def update_product(request: Request, id: int = Form(...), product_image: UploadFile = File(...), name: str = Form(...),
                         price: int = Form(...), description: str = Form(...),
                         category_id: int = Form(...), subcategory_id: int = Form(...),
                         discountprice: int = Form(...)):
    user = await Add_products.get(id=id)

    FILEPATH = "static/product"
    filename = product_image.filename
    extension = filename.split(".")[1]
    imagename = filename.split(".")[0]
    if extension not in ["png", "jpg", "jpeg"]:
        return {"status": "error", "detial": "File extension not allowed"}
    dt = datetime.now()
    dt_timestamp = round(datetime.timestamp(dt))
    modified_image_name = imagename+"_"+str(dt_timestamp)+"."+extension
    genrated_name = FILEPATH + modified_image_name
    file_content = await product_image.read()
    with open(genrated_name, "wb") as file:
        file.write(file_content)
    file.close()

    update_product = await Add_products.filter(id=id).update(product_image=genrated_name,
                                                             name=name,
                                                             price=price,
                                                             description=description,
                                                             category_id=category_id,
                                                             subcategory_id=subcategory_id,
                                                             discountprice=discountprice)
    return RedirectResponse("/adminAllproducts/", status_code=status.HTTP_302_FOUND)


@router.get("/delete_product/{id}")
async def delete_cartproducts(request: Request, id: int):
    delete_products = await Add_products.get(id=id).delete()

    return RedirectResponse("/adminAllproducts/", status_code=status.HTTP_302_FOUND)


@router.get("/adminenquiries/", response_class=HTMLResponse)
async def read_item(request: Request):
    if "user_id" not in request.session:
        flash(request, "Login required", "danger")
        return RedirectResponse("/adminlogin/", status_code=status.HTTP_302_FOUND)
    else:
        user = await Register_admin.all()
        return templates.TemplateResponse("enquiries.html", {"request": request, "user": user})
