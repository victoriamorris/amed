#  -*- coding: utf8 -*-
import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s]\t{%(pathname)s:%(lineno)d}\t%(levelname)s\t%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='amed.log',
                    filemode='w')
logger = logging.getLogger()
