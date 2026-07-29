import fire


def hello(name: int):
    return f"Hello {name}!"


if __name__ == "__main__":
    fire.Fire(hello)
