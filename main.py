# coding=utf-8

import automatizacionGUI
import sys

def main():
    # Punto de entrada
    try:
        obj = automatizacionGUI()
        obj.__init__()
    except Exception as e:
        #print(e)
        sys.exit(0)

if __name__ == '__main__':
    main()