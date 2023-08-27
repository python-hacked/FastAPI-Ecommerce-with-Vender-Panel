from configs.connection import DATABASE_URL 

db_url = DATABASE_URL()

TORTOISE_ORM= {
        "connections": {"default":db_url},
        "apps": {
             "models": {
            "models": ["ecom_API.models","aerich.models","ecom_admin.models",],
            "default_connection": "default",
             },
        },

    }
