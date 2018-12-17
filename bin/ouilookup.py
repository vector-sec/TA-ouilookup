#!/opt/splunk/bin/python
# Copyright (C) 2018 vector_sec -- https://twitter.com/vector_sec
#
import splunk.Intersplunk
import os
import time
import logging
import logging.handlers
from manuf import manuf


# http://dev.splunk.com/view/logging/SP-CAAAFCN
def setup_logging():
    logger = logging.getLogger('splunk.ta-ouilookup')
    logger.setLevel(logging.ERROR)  # Change to INFO, DEBUG, ERROR as needed

    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    LOGGING_FILE_NAME = "ta-ouilookup.log"
    BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
    LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
    splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a') 
    splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(splunk_log_handler)
    splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
    return logger


def get_manuf_parser():
    if not os.path.isfile("manuf.db") or not os.path.isfile("manuf.db.timestamp"):
        logger.debug("Missing manuf.db or manuf.db.timestamp. Rebuilding database")
        open("manuf.db", "a").close()
        mac_parser = manuf.MacParser(manuf_name="manuf.db")
        mac_parser.update()
        with open("manuf.db.timestamp", 'w') as f:
            f.write(str(int(time.time())))
        return mac_parser
    else:
        with open("manuf.db.timestamp", 'r') as f:
            last_update = f.read()
            last_update = int(last_update)
            now = int(time.time())
            if now - last_update >= 86400:
                logger.debug("manuf.db is older than 24 hours, updating")
                mac_parser = manuf.MacParser(manuf_name="manuf.db")
                mac_parser.update()
                with open("manuf.db.timestamp", 'w') as f:
                    f.write(str(int(time.time())))
                return mac_parser
            else:
                logger.debug("using cached manuf.db")
                mac_parser = manuf.MacParser(manuf_name="manuf.db")
                return mac_parser


try:
    logger = setup_logging()
    parser = get_manuf_parser()
    new_results = []

    logger.info('getting Splunk options...')  # logger
    # get key value pairs from user search
    keywords, options = splunk.Intersplunk.getKeywordsAndOptions()
    logger.info('got these options: %s ...' % (options))  # logger
    # get user option or use a default value
    field = options.get('field', 'src_mac')
    logger.info('got these options: field = %s ...' % (field))  # logger

    logger.info("Getting Splunk results ...")
    results, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()
    logger.debug(results)

    for line in results:
        try:
            line['manuf'] = parser.get_manuf(line[field])
            line['manuf_long'] = parser.get_manuf_long(line[field])
        except ValueError:
            line['manuf'] = "Unknown"
            line['manuf_long'] = "Unknown"
        new_results.append(line)

    splunk.Intersplunk.outputResults(new_results)

except:
    import traceback
    stack = traceback.format_exc()
    results = splunk.Intersplunk.generateErrorResults("Error : Traceback: " + str(stack))