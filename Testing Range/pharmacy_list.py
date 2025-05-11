import csv

class pharmacy_list:
    def check_pharmacy(self) -> list[list[str]]:
        pharmacy_list = []
        with open('../Data/pharmacy_location.csv', mode='r', encoding='utf-8-sig') as file:
            csvFile = csv.reader(file)
            next(csvFile)
            for lines in csvFile:
                lines = [cell.lower() for cell in lines]
                lines.append(lines[2] + ", " + lines[0])
                pharmacy_list.append(lines)
        for pharmacy in pharmacy_list:
            print(pharmacy)
        return pharmacy_list

if __name__ == "__main__":
    p = pharmacy_list()
    p.check_pharmacy()
