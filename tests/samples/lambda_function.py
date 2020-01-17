import snoop


def main():
    my_function = snoop.snoop()(lambda x: x ** 2)
    my_function(3)


if __name__ == '__main__':
    main()
