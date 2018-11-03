if __name__ == "__main__" and __package__ is None:
    from sys import path
    from os.path import dirname as dir

    path.append(dir(path[0]))
    __package__ = 'new-episode'

from test_scraping import run_fake_web_server


run_fake_web_server()
