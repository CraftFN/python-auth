async def authenticate():

    base = "https://www.epicgames.com"
    base_public_service = "https://account-public-service-prod03.ol.epicgames.com"
    launcher_token = "MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE=" 
    fortnite_token = "ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ="
    email = "YOUR EMAIL HERE"
    password = "YOUR PASSWORD HERE"
    
    with requests.Session() as session:
        session.get(f"{base}/id/api/csrf")

        res = session.post(
            f"{base}/id/api/login", 
            headers={
                "x-xsrf-token": session.cookies.get("XSRF-TOKEN")
            },
            data={
                "email": email,
                "password": password,
                "rememberMe": False
            },
            cookies=session.cookies
        )
        
        if res.status_code == 400:
            raise ValueError("Wrong email/password entered.")
            
        if res.status_code == 431:
            session.get(f"{base}/id/api/csrf")

            res = session.post(
                f"{base}/id/api/login/mfa",
                headers={
                    "x-xsrf-token": session.cookies.get("XSRF-TOKEN")
                },
                data={
                    "code": two_factor_code or input("Please enter the 2fa code: "),
                    "method": "authenticator",
                    "rememberDevice": False
                },
                cookies=session.cookies
            )
            
            if res.status_code == 400:
                raise ValueError("Wrong 2fa code entered.")
        
        res = session.get(
            f"{base}/id/api/exchange", 
            headers={
                "x-xsrf-token": session.cookies.get("XSRF-TOKEN")
            },
            cookies=session.cookies
        )
        exchange_code = res.json()["code"]

        res = session.post(
            f"{base_public_service}/account/api/oauth/token", 
            headers={
                "Authorization": f"basic {launcher_token}"
            },
            data={
                "grant_type": "exchange_code",
                "exchange_code": exchange_code,
                "token_type": "eg1"
            }
        )
        launcher_access_token = res.json()["access_token"]
        
        res = session.get(
            f"{base_public_service}/account/api/oauth/exchange",
            headers={
                "Authorization": f"Bearer {launcher_access_token}"
            }
        )
        exchange_code = res.json()["code"]

        res = session.post(
            f"{base_public_service}/account/api/oauth/token",
            headers={
                "Authorization": f"basic {fortnite_token}"
            },
            data={
                "grant_type": "exchange_code",
                "token_type": "eg1",
                "exchange_code": exchange_code
            }
        )
        
        fortnite_access_token = res.json()["access_token"]
        return fortnite_access_token