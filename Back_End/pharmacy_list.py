from dotenv import load_dotenv
import csv
import requests
import time
import os
import re

class pharmacy_list:
    def __init__(self):
        self.pharmacy_address_list = []

    def check_pharmacy_address_list(self, pharmacy_address) -> list[str]:
        for i in range(len(self.pharmacy_address_list)):
            if pharmacy_address in self.pharmacy_address_list[i][2]:
                print(i)
                return [self.pharmacy_address_list[i][0], self.pharmacy_address_list[i][1]]

    def get_pharmacy_address_list(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(BASE_DIR, '..', 'Data', 'Ontario_Pharmacy_Information.csv')
        with open(csv_path, mode='r', encoding='utf-8-sig') as file:
            csvFile = csv.reader(file)
            title_line = next(csvFile)
            for lines in csvFile:
                #print(lines[11])
                self.pharmacy_address_list.append([lines[3], lines[4], lines[11]])


    def normalize_address(self, address):
        import os
        load_dotenv()
        API_KEY = os.getenv("Google_Geocoding_API_KEY")
        url1 = "https://maps.googleapis.com/maps/api/geocode/json?address="
        url2 = "&key="
        url = url1 + address + url2 + API_KEY
        params = {
            "q": address,
            "format": "json",
            "addressdetails": 1
        }
        response = requests.get(url, params=params, headers={'User-Agent': 'MyApp'})
        data = response.json()
        address_dict = data['results']
        return address_dict[0]['formatted_address'] if address_dict else None

    #a1 = normalize_address("10 Downing St, London")
    #a2 = normalize_address("Ten Downing Street, Westminster, London")


    def check_pharmacy(self) -> list[list[str]]:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(BASE_DIR, '..', 'Data', 'Ontario_Pharmacy_Information.csv')
        pharmacy_list = []
        with open('csv_path', mode='r', encoding='utf-8-sig') as file:
            csvFile = csv.reader(file)
            next(csvFile)
            for lines in csvFile:
                line_1 = re.sub(r'[^A-Za-z0-9\'\- ]', ' ', lines[5])
                line_2 = re.sub(r'[^A-Za-z0-9\- ]', '', lines[6])
                postal_code = lines[7]
                address = None
                if line_2 == "" or "box" in line_2.lower():
                    address = line_1 + "," + lines[7] + ",ON,CANADA"
                    k = self.normalize_address(address)
                else:
                    address1 = line_1 + "," + line_2 + "," + lines[7] + ",ON,CANADA"
                    address2 = line_1 + "," + lines[7] + ",ON,CANADA"
                    k1 = self.normalize_address(address1)
                    k2 = self.normalize_address(address2)
                    if len(k2) > len(k1):
                        k = k2
                    else:
                        k = k1
                lines.append(k)
                pharmacy_list.append(lines)
        for pharmacy in pharmacy_list:
            print(pharmacy)
        return pharmacy_list

    def update_pharmacy_list(self) -> list[list[str]]:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(BASE_DIR, 'Data', 'Ontario_Pharmacy_Information.csv')
        pharmacy_list = []
        with open(csv_path, mode='r', encoding='utf-8-sig') as file:
            csvFile = csv.reader(file)
            title_line = next(csvFile)
            for lines in csvFile:
                line_1 = re.sub(r'[^A-Za-z0-9\'\- ]', ' ', lines[5])
                find_po = line_1.lower().find("po box")
                if find_po > 0:
                    line_1 = line_1[:find_po]
                line_2 = re.sub(r'[^A-Za-z0-9\- ]', '', lines[6])
                community = lines[7]
                postal_code = lines[7]
                address = None
                find_unit = line_1.lower().find("unit")
                if find_unit > 0:
                    line_2 = line_1[find_unit:]
                    line_1 = line_1[:find_unit]
                if line_2 == "" or "box" in line_2.lower():
                    address = line_1 + "," + community + ",ON,CANADA," + postal_code
                    k = self.normalize_address(address)
                else:
                    address1 = line_1 + "," + line_2 + "," + community + ",ON,CANADA," + postal_code #remove postal code if not working
                    address2 = line_1 + "," + community + ",ON,CANADA," + postal_code
                    k1 = self.normalize_address(address1)
                    k2 = self.normalize_address(address2)
                    if len(k2) > len(k1):
                        k = k2
                    else:
                        k = k1
                lines.append(k)
                print(k)
                pharmacy_list.append(lines)
        for pharmacy in pharmacy_list:
            print(pharmacy)
        with open('csv_path', 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(title_line)
            writer.writerows(pharmacy_list)
        return pharmacy_list

    #def write_csv_address(self):


if __name__ == "__main__":
    p = pharmacy_list()
    r = p.normalize_address("107 Jonathon Cheechoo Drive,Moose Factory,ON,CANADA")
    print(r)
    r = p.normalize_address("UNIT 8-1170 BURNHAMTHORPE RD. W.")
    print(r)
    #p.update_pharmacy_list()
    p.get_pharmacy_address_list()
    print(p.check_pharmacy_address_list("300 Main St W, Kingsville, ON N9Y 1H8, Canada"))
    #print(p.check_pharmacy_address_list(r))
