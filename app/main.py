# coding=utf-8

import automatizacionGUI
import sys

# Punto de entrada
if __name__ == '__main__':
    try:
        obj = automatizacionGUI()
        obj.__init__()
    except Exception as e:
        #print(e)
        sys.exit(0)