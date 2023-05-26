class Multiplication:
    def __init__(self, left: int, right: int) -> None:
        self.left = left
        self.right = right

    def compute(self) -> int:
        return self.left * self.right


def main():
    if Multiplication(2, 3).compute() >= 10:
        print('hello world')
    else:
        print('hello Mars')


main()
