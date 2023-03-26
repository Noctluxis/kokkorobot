import kokkoro


kokkoro.init()
app = kokkoro.asgi()

if __name__ == "__main__":
    kokkoro.run('run:app')
