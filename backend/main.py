import typer


def main(name: str):
    print(f"Hello {name} from backend!")


if __name__ == "__main__":
    typer.run(main)
