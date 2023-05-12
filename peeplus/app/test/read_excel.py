import xlrd


def read_excel():
    file_path = "/Users/movi/Desktop/事故4(2).xls"
    clinic_file = xlrd.open_workbook(file_path)
    sheet_names = clinic_file.sheet_names()

    event_ls = []
    for name in sheet_names:
        sheet = clinic_file.sheet_by_name(name)
        rows = sheet.get_rows()
        for row in rows:
            event = {}
            event["type"] = name
            event["name"] = row[0].value
            event["introduction"] = row[1].value
            event["url"] = row[2].value
            event["process"] = row[3].value
            event_ls.append(event)
    print(event_ls)


if __name__ == '__main__':
    read_excel()