import csv
from itertools import groupby


def validate_row(row: list, line_num: int, columns: list, verbose=True):
    errors = []
    if len(row) != len(columns):
        if verbose:
            print(
                f"Строка {line_num}: ожидается {len(columns)} колонок, "
                f"получено {len(row)}"
            )
        return None

    row = [value.strip() for value in row]

    for column, value in zip(columns, row):
        if not value:
            errors.append(
                f"Строка {line_num}: пустое поле «{column}»"
            )
    try:
        salary = int(row[5])
        if salary < 0:
            errors.append(f"Строка {line_num}: оклад не может быть отрицательным")
    except ValueError:
        errors.append(
            f"Строка {line_num}: оклад должен быть целым числом"
        )
    if len(errors) == 0:
        return row
    else:
        if verbose:
            print("Строка не валидна:", *errors)
        return None


def read_data(filename="Corp_Summary.csv", verbose=True):
    rows = list()

    with open(filename, encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter=";")
        columns = next(reader, [])

        if len(columns) != 6:
            if verbose:
                print("В заголовке файла должно быть 6 колонок")
            return rows

        for line_num, row in enumerate(reader, start=2):
            checked_row = validate_row(
                row, line_num, columns, verbose=verbose
            )
            if checked_row is not None:
                rows.append(checked_row)
    return rows


def do_report_1(rows: list):
    sorted_rows = sorted(rows, key=lambda x: x[1])
    report = list()
    for department, group in groupby(sorted_rows, key=lambda row: row[1]):
        teams = sorted({row[2] for row in group})
        report.append([department, teams])
    return report


def do_report_2(rows: list):
    sorted_rows = sorted(rows, key=lambda x: x[1])
    report = list()
    for department, group in groupby(sorted_rows, key=lambda row: row[1]):
        curr_group = list(group)
        max_val = max(int(row[5]) for row in curr_group)
        mean_val = sum(int(row[5]) for row in curr_group) / len(curr_group)
        min_val = min(int(row[5]) for row in curr_group)
        report.append([department, len(curr_group),
                       min_val, max_val, mean_val])
    return report


def do_report_3(rows: list, output: str):
    report = do_report_2(rows)
    with open(output, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(report)


def do_report(var_num: int, rows: list, output="output.csv"):
    if var_num == 1:
        return do_report_1(rows)
    elif var_num == 2:
        return do_report_2(rows)
    elif var_num == 3:
        return do_report_3(rows, output=output)
    else:
        print("Неверно введён тип отчёта")


if __name__ == "__main__":
    rows = read_data("Corp_Summary.csv")
    report1 = do_report(var_num=1, rows=rows)
    print(report1)
    report2 = do_report(var_num=2, rows=rows)
    print(report2)
    do_report(var_num=3, rows=rows)
