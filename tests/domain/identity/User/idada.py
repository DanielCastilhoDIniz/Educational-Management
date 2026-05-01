from datetime import UTC, date, datetime, timedelta

hoje = datetime.now(UTC)


nascimento = date(date.today().year - 18, hoje.month, hoje.day)


if "__main__" == __name__:
    print(f"Hoje: {hoje}")
    print(f"Nascimento: {nascimento}")
    idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
    print(f"Idade: {idade}")