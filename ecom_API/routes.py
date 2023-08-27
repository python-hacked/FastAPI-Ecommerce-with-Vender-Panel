from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi_login import LoginManager
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi import APIRouter
from ecom_API.pydantic_models import *
from . models import *
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from fastapi_login.exceptions import InvalidCredentialsException
from starlette.middleware.sessions import SessionMiddleware
import typing
import re

router = APIRouter()


def flash(request: Request, message: typing.Any, category: str = "") -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append(
        {"message": message, "category": category})


def get_flashed_messages(request: Request):
    print(request.session)
    return request.session.pop("_messages") if "_messages" in request.session else []


BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory="ecom_API/templates")
templates.env.globals['get_flashed_messages'] = get_flashed_messages
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET = 'your-secret-key'
manager = LoginManager(SECRET, token_url='/auth/token')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@router.get("/registration/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request, })


@router.post('/registration/',)
async def create_user(request: Request, email: EmailStr = Form(...),
                      name: str = Form(...),
                      phone: str = Form(...),
                      password: str = Form(...),
                      city: str = Form(...),
                      address: str = Form(...)):
    reg_pass = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat_pass = re.compile(reg_pass)
    mat_pass = re.search(pat_pass, password)

    reg_name = re.compile('^[A-Za-z]+$')
    mat_name = re.search(reg_name, name)

    if await Create_user.filter(email=email).exists():
        flash(request, "Email already exists", "danger")
        return RedirectResponse("/registration/", status_code=status.HTTP_302_FOUND)
    elif await Create_user.filter(phone=phone).exists():
        flash(request, "Phone number already exists", "danger")
        return RedirectResponse("/registration/", status_code=status.HTTP_302_FOUND)
    else:
        if not mat_name:
            flash(request, "Your name can be in latters only ", "danger")
            return RedirectResponse("/registration/", status_code=status.HTTP_302_FOUND)
        elif len(phone) != 10:
            flash(request, "Please enter 10 digit number", "danger")
            return RedirectResponse("/registration/", status_code=status.HTTP_302_FOUND)
        elif not mat_pass:
            flash(request, "Your password lenth must be in 6 to 20 and must contain atleast one uppercase, one lower case, one special character, one number ", "danger")
            return RedirectResponse("/registration/", status_code=status.HTTP_302_FOUND)
        else:
            user_obj = await Create_user.create(email=email, name=name,
                                                phone=phone, city=city, address=address, password=get_password_hash(password))
            print(user_obj)
            flash(request, "Registration successfully", "success")
            return RedirectResponse("/login/", status_code=status.HTTP_302_FOUND)


@router.get("/login/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, })


@router.post('/address/',)
async def create_add(request: Request,
                     name: str = Form(...), address: str = Form(...),
                     city: str = Form(...), pincode: str = Form(...),
                     phone: str = Form(...), state: str = Form(...),
                     ):
    orderuser_id = request.session["user_id"]
    if await Address.create(name=name, phone=phone, address=address,
                            city=city, orderuser_id=orderuser_id, pincode=pincode, state=state):
        return RedirectResponse("/checkout/", status_code=status.HTTP_302_FOUND)


@manager.user_loader()
async def load_user(email: str):
    if await Create_user.exists(email=email):
        newapi1 = await Create_user.get(email=email)
        return newapi1


@router.post('/login/', )
async def login(request: Request, email: str = Form(...),
                password: str = Form(...)):

    email = email
    user = await load_user(email)

    if not Create_user:
        flash(request, "User not exsist", "danger")
        return RedirectResponse("/login/", status_code=status.HTTP_302_FOUND)
    elif not verify_password(password, user.password):
        flash(request, "Failed to login", "danger")
        return RedirectResponse("/login/", status_code=status.HTTP_302_FOUND)
    else:
        request.session["user_id"] = user.id
        request.session["user_name"] = user.name
        request.session["user_phone"] = user.phone
        request.session["user_email"] = user.email

        print(request.session["user_id"])

        print(request.session["user_name"])
        flash(request, "Login successfully", "success")
        return RedirectResponse("/welcome/", status_code=status.HTTP_302_FOUND)


@router.get('/logout/', )
async def logout(request: Request,):
    request.session.clear()
    return RedirectResponse("/login/", status_code=status.HTTP_302_FOUND)


@router.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    addp = await Add_products.all()

    return templates.TemplateResponse("index.html", {"request": request, 'addp': addp})


@router.get("/category/", response_class=HTMLResponse)
async def read_item(request: Request):
    ct = await Category.all()
    sct = await SubCategory.all()
    addp = await Add_products.all()
    return templates.TemplateResponse("category.html", {"request": request, 'ct': ct, 'sct': sct, 'addp': addp})


@router.get("/filter/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: int):
    addp = await Add_products.all()
    sct = await SubCategory.get(id=id)

    ct = await Category.all()
    scts = await SubCategory.all()
    return templates.TemplateResponse("productfilter.html", {"request": request, 'sct': sct, 'addp': addp, 'ct': ct, 'scts': scts})


@router.get("/product/{slug:str}/", response_class=HTMLResponse)
async def read_item(request: Request, slug: str):
    addp = await Add_products.get(slug=slug).select_related("category")
    product = await Add_products.filter(slug=slug)
    return templates.TemplateResponse("single-product.html", {"request": request, "addp": addp, "product": product})


@router.get("/cart/", response_class=HTMLResponse)
async def read_item(request: Request):
    add_to_cart = await Addtocart.all().select_related("product_d", "user")
    return templates.TemplateResponse("cart.html", {"request": request, "add_to_cart": add_to_cart})


@router.post('/addtocart/',)
async def create_cart(request: Request, product_d_id: int = Form(...),):

    user_id = request.session["user_id"]
    if await Addtocart.filter(product_d_id=product_d_id).exists():
        return RedirectResponse("/cart/", status_code=status.HTTP_302_FOUND)
    else:
        cart_obj = await Addtocart.create(user_id=user_id, product_d_id=product_d_id)
    return RedirectResponse("/cart/", status_code=status.HTTP_302_FOUND)


@router.post('/order/',)
async def create_order(request: Request, product_d_id: List[int] = Form(...),
                       shipping: float = Form(...),
                       subtotal: float = Form(...),
                       total: float = Form(...),
                       quantity: List[str] = Form(...),):
    orderuser_id = request.session["user_id"]
    list_lengths = [len(product_d_id), len(quantity)]
    clr = await Order.get(orderuser_id=orderuser_id).delete()
    if len(set(list_lengths)) != 1:
        return HTTPException(status_code=400, detail="The lists must have the same length")
    for i in range(len(quantity)):
        await Order.create(orderuser_id=orderuser_id, shipping=shipping,
                           product_d_id=product_d_id[i], subtotal=subtotal, total=total, quantity=quantity[i])
    return RedirectResponse("/checkout/", status_code=status.HTTP_302_FOUND)


@router.post('/billing/',)
async def create_bill(request: Request, ostatus_id: int = Form(...),
                      productname: str = Form(...),
                      total: str = Form(...),
                      orderuser_id: str = Form(...), 
                      addressuser_id: str = Form(...),
                     qty: str = Form(...),):
    orderuser_id = request.session["user_id"]
    deletecart = await Addtocart.get(user_id=orderuser_id).delete()

    if await Checkout.create(addressuser_id=addressuser_id,
                            total=total,
                            orderuser_id=orderuser_id, 
                            qty=qty, 
                            ostatus_id=ostatus_id, 
                            productname=productname):
        return RedirectResponse("/confirmation/", status_code=status.HTTP_302_FOUND)


@router.get("/checkout/", response_class=HTMLResponse)
async def read_item(request: Request):
    totals = await Order.all().select_related("product_d", "orderuser")
    users = await Create_user.all()
    add = await Address.all()
    for t in totals:
        if request.session['user_id'] == t.orderuser_id:
            subtotal_amount = t.subtotal
            total_amount = t.total

    return templates.TemplateResponse("checkout.html", {"request": request, "totals": totals, "users": users, "add": add, "total_amount": total_amount, "subtotal_amount": subtotal_amount})

@router.post('/orderhistory/',)
async def create_orderhistory(request: Request, ostatus_id: int = Form(...),
                      productname: str = Form(...),
                      total: str = Form(...),
                      orderuser_id: str = Form(...), 
                      addressuser_id: str = Form(...),
                     qty: str = Form(...),):
                     
    orderuser_id = request.session["user_id"]
    clra = await Checkout.all().delete()
    

    if await Orderhitory.create(addressuser_id=addressuser_id,
                            total=total,
                            orderuser_id=orderuser_id, 
                            qty=qty, 
                            ostatus_id=ostatus_id, 
                            productname=productname):
        return RedirectResponse("/tracking/", status_code=status.HTTP_302_FOUND)

@router.delete("/delete_cartitem/{id}")
async def delete_cartproducts(request: Request, id: int):
    delete_products = await Addtocart.get(id=id).delete()

    return JSONResponse({'success': True})


@router.get("/confirmation/", response_class=HTMLResponse)
async def read_item(request: Request):
    totals = await Order.all().select_related("product_d", "orderuser")
    billing = await Checkout.all().select_related("addressuser")
    add = await Address.all()
    for t in totals:
        if request.session['user_id'] == t.orderuser_id:
            total_amount = t.total
    return templates.TemplateResponse("confirmation.html", {"request": request, "totals": totals, "billing": billing, "total_amount": total_amount,"add":add})


@router.get("/tracking/", response_class=HTMLResponse)
async def read_item(request: Request):
    billings = await Orderhitory.all().select_related("ostatus")
    orders = await Orderhitory.all().select_related("orderuser","addressuser","ostatus")


    return templates.TemplateResponse("tracking.html", {"request": request, "billings": billings,"orders":orders})


@router.get("/profiledetail/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request, })


@router.get("/welcome/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request, })


@router.get("/address/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("address.html", {"request": request, })
