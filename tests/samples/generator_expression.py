import snoop


@snoop(depth=2)
def main():
    return list(x * 2 for x in [1, 2])


if __name__ == '__main__':
    main()
