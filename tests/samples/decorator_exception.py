import snoop


@snoop
def main():
    try:
        @int
        def foo():
            pass
    except:
        pass


if __name__ == '__main__':
    main()
