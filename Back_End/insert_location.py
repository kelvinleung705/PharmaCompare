
import pymongo
import certifi
from dotenv import load_dotenv
import requests
import os


class insert_location:
    def __init__(self):
        load_dotenv()
        mongoDB_Username = os.getenv("MongoDB_Username")
        mongoDB_Password = os.getenv("MongoDB_Password")
        #myclient = pymongo.MongoClient("mongodb+srv://"+mongoDB_Username+":"+mongoDB_Password+"@pharmacomparedata1.tu3p29k.mongodb.net/?retryWrites=true&w=majority&appName=PharmaCompareData1")
        myclient = pymongo.MongoClient(
            "mongodb+srv://" + mongoDB_Username + ":" + mongoDB_Password + "@pharmacomparedata1.tu3p29k.mongodb.net/?retryWrites=true&w=majority&appName=PharmaCompareData1",
            tls=True,
            tlsCAFile=certifi.where()
        )
        self.database = myclient["Drug_Price"]
        self.pharmacy_list = self.database["pharmacy_drug_list"]


    def add_location_to_all(self):
        pharmacies_no_location = self.pharmacy_list.find({ "latitude": { "$exists": False } })
        for pharmacy in pharmacies_no_location:
            self.add_location_to_one(pharmacy["pharmacy address"], pharmacy["pharmacy ident"])

    def add_location_to_one(self, address: str, pharmacy_ident:str):
        import os
        load_dotenv()
        API_KEY = os.getenv("Google_Geocoding_API_KEY")
        url1 = "https://maps.googleapis.com/maps/api/geocode/json?address="
        url2 = "&key="
        url = url1 + address.replace("#", " ") + url2 + API_KEY
        params = {
            "q": address,
            "format": "json",
            "addressdetails": 1
        }
        response = requests.get(url, params=params, headers={'User-Agent': 'MyApp'})
        data = response.json()
        address_dict = data['results']
        if address_dict and len(address_dict) > 0 and "navigation_points" in address_dict[0].keys():
            location = address_dict[0]['navigation_points'][0]["location"]
            latitude = location["latitude"]
            longitude = location["longitude"]
            self.pharmacy_list.update_one(
                {
                    "pharmacy ident": pharmacy_ident
                },
                {"$set":
                    {"latitude": latitude, "longitude": longitude
                    }
                }
            )

if __name__ == "__main__":
    job = insert_location()
    job.add_location_to_all()

