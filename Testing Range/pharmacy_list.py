import csv
import requests
import time

class pharmacy_list:
    def normalize_address(self, address):
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "addressdetails": 1
        }
        response = requests.get(url, params=params, headers={'User-Agent': 'MyApp'})
        data = response.json()
        return data[0] if data else None

    #a1 = normalize_address("10 Downing St, London")
    #a2 = normalize_address("Ten Downing Street, Westminster, London")


    def check_pharmacy(self) -> list[list[str]]:
        pharmacy_list = []
        with open('../Data/Ontario_Pharmacy_Locations.csv', mode='r', encoding='utf-8-sig') as file:
            csvFile = csv.reader(file)
            next(csvFile)
            for lines in csvFile:
                address = None
                if lines[6] == "":
                    address = lines[5] + ", " + lines[7] + ", ON, CANADA"
                else:
                    address = lines[5] + ", " + lines[6] + ", " + lines[7] + ", ON, CANADA"

                k = self.normalize_address(address)
                lines.append(k)
                pharmacy_list.append(lines)
        for pharmacy in pharmacy_list:
            print(pharmacy)
        return pharmacy_list

if __name__ == "__main__":
    p = pharmacy_list()
    r = p.normalize_address("1 Dodds Gate, Markham, ON, CANADA")
    p.check_pharmacy()
