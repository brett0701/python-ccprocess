import logging
import inotify.adapters
import sys
import websocket
import ssl
import json
import os
import time
import datetime


def configure_logging(baseDir):
    global logger
    logger = logging.getLogger('wsmonitor')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    now = datetime.datetime.now()
    ch = logging.FileHandler('/var/log/cc/' + baseDir + "-" +
                             str(now.month) + str(now.day) + str(now.year) + '.lg')
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    logger.info("")
    logger.info("Starting Logging")


def process_file(ws, filename):
    responseFile = filename.replace("request", "response")
    enabledevice = {"Request": "EnableCardReader", "readers": "MCS", "prompt": "", "transactionType": "SALE", "transactionSuperType": "Credit", "amount": "5.00", "ManualMode": "0", "preventPartial": "1",
                    "SigFlag": "1", "accountId": "", "V": "1", "M": "1", "D": "1", "A": "1", "AdditionalData": [{"mid": ""}, {"tid": ""}, {"bankId": ""}, {"transId": ""}, {"cashBack": ""}, {"stin": ""}, {"lcp": "VAL"}]}
    canceltransaction = {"Request": "TransCancel"}
    if ws.connected:
        logger.info("Processing file: " + filename)
        try:
            file = open(filename, "r")
            lines = file.readlines()
            transactionType = lines[1].strip()
            if transactionType == "Sale":
                enabledevice['transactionType'] = lines[1].strip()
                enabledevice['accountId'] = lines[2].strip()
                enabledevice['AdditionalData'][3]['transId'] = lines[3].strip()
                enabledevice['transactionSuperType'] = lines[4].strip()
                enabledevice['amount'] = lines[5].strip()
                enabledevice['prompt'] = "Please Tap, Swipe or Insert " + \
                    lines[3].strip()
            file.close()
        except IOError as e:
            logger.error(
                "I/O error({0}): {1} {2}".format(e.errno, e.strerror, filename))
            return
        if transactionType == "Sale":
            logger.info("Enabling device...")
            logger.debug(enabledevice)
            time.sleep(2)
            ws.send(json.dumps(enabledevice))
            while True:
                result = json.loads(ws.recv())
                if not result:
                    break
                if 'Response' in result and result['Response'] != "CardRead":
                    errorMsg = ""
                    if 'AuthResponseText' in result or result['Response'] == "AuthorizationResponse":
                        '''
                        print("Checking status..")
                        print("Status: ")
                        print(result['Status'])  
                        '''

                        if int(result['Status']) != 1:
                            logger.info(
                                "Transaction Cancelled, Declined, Error, Network Timeout")
                            errorMsg = result['AuthResponseText']
                            if int(result['Status']) == 3:
                                while True:
                                    result = json.loads(ws.recv())
                                    logger.debug(result)
                                    if result['Message'] == "Receipt Data Sent Successfully":
                                        break
                            else:
                                while True:
                                    result = json.loads(ws.recv())
                                    logger.debug(result)
                                    if result['Message'] == "Chip Card Removed":
                                        break
                                    if result['Response'] == "AuthorizationResponse":
                                        break
                            break
                        else:
                            logger.info("Assigning authorizationResponse")
                            logger.debug(result)
                            authorizationResponse = result
                if 'Message' in result:
                    logger.debug(result['Message'])
                    if result['Message'] == "Receipt Data Sent Successfully":
                        logger.debug(result)
                        break
                    if result['Message'] == "Terminal is not ready":
                        errorMsg = result['Message']
                        break
                    if result['Message'] == "Transaction Cancelled":
                        errorMsg = result['Message']
                        break
                        '''
                        logger.debug(result)
                        errorMsg = "Transaction Cancelled " + errorMsg
                        logger.info(errorMsg)
                        while True:
                            result = json.loads(ws.recv())
                            logger.debug(result)
                            if result['Message'] == "Chip Card Removed":
                               break
                            if result['Response'] == "AuthorizationResponse":
                               break
                        logger.info("Transaction Cancelled breaking")
                        break
                        '''
        logger.error("Error Msg: " + errorMsg)
        if errorMsg != "":
            createfile(responseFile, errorMsg, "Y")
        else:
            createfile(responseFile, authorizationResponse, "N")
        return
        if transactionType == "Cancel":
            logging.info("Canceling Transaction...")
            ws.send(json.dumps(canceltransaction))
            result = json.loads(ws.recv())
            logging.debug(result['Message'])
            errorMsg = result['Message']
            createfile(responseFile, errorMsg, "Y")
            return
    else:
        logging.error("Websocket is not connected.")
        return


def initialize_device(deviceName):
    # deviceName = "Device 00000008"
    initialdevice = {"Request": "InitializeTerminal",
                     "RequestType": "System", "terminal": {"deviceId": ""}}

    initialdevice['terminal']['deviceId'] = deviceName
    logger.info("Initializing device...")
    logger.debug(initialdevice)
    time.sleep(5)
    ws.send(json.dumps(initialdevice))
    result = json.loads(ws.recv())
    logger.info(result['Message'])
    if result['Message'] == "Device failed to initialize":
        logger.error("Device failed to initialize")
    return


def createfile(responseFile, result, error):
    try:
        logger.info("Creating response file: " + responseFile)
        logger.info(result)
        f = open(responseFile, "w")
        if error == "Y":
            f.write("Error: " + result + "\n")
            f.write("Approval Code: " + "\n")
            f.write("Partial Auth: " + "\n")
            f.write("Auth Amount: " + "\n")
            f.write("Auth #: " + "\n")
            f.write("Token: " + "\n")
        elif result['AuthResponseText'] == "Approved":
            if result['PartialAuth'] == "0":
                # if result['ParialAuth'] == "0":
                partialAuth = "No"
            else:
                partialAuth = "Yes"
            logger.info("Partial Auth: " + partialAuth)
            remainingAmt = result['RemainingAmount']
            if remainingAmt == "":
                remainingAmt = "0"
            authorizedAmount = float(
                result['OriginalAuthAmount']) - float(remainingAmt)
            authorizedAmount = (authorizedAmount / 100)
            logger.info("Writing to response file")
            f.write("Error: " + "\n")
            f.write("Approval Code: " + result['ApprovalCode'] + "\n")
            f.write("Partial Auth: " + partialAuth + "\n")
            f.write("Auth Amount: " +
                    str("{0:.2f}".format(authorizedAmount)) + "\n")
            f.write("Reference #: " +
                    result['AdditionalData'][0]['reference_number'] + "\n")
            f.write("Token: " + result['Token'] + "\n")
        else:
            f.write("Error: " + result['Message'] + "\n")
            f.write("Approval Code: " + "\n")
            f.write("Partial Auth: " + "\n")
            f.write("Auth Amount: " + "\n")
            f.write("Auth #: " + "\n")
            f.write("Token: " + "\n")
        f.close()
        logger.info("Done Writing to response file")
    except IOError as e:
        logger.error(
            "I/O error({0}): {1} {2}".format(e.errno, e.strerror, filename))
    finally:
        return


def connect_ws():
    global ws
    try:
        time.sleep(2)
        ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        # ws.connect("wss://192.168.0.200:8888")
        ws.connect("wss://localhost:8888")
        result = json.loads(ws.recv())
        logger.info(result['Message'])
        result = json.loads(ws.recv())
        if ('Message' in result and
                result['Message'] == "Terminal Implementation NOT Present!"):
            logger.info("There are no cc terminals found on the network")
            logger.info(
                "Disconnecting from FAPs websocket and stopping monitor")
            disconnect_ws(ws)
            logger.info("Monitor Stopped")
            sys.exit()
        try:
            for index, element in enumerate(result):
                logger.info(result['devices'][index]['deviceId'])
        except IndexError:
            pass
    except:
        logger.error(
            "Error connecting to jSTL websocket. Verify it is running")
        sys.exit()


def disconnect_ws(ws):
    if ws.connected:
        try:
            ws.close()
        except:
            logger.error("Could not stop websocket server")
    else:
        logger.error("Disconnected From Websocket")


def _main(watchDir):
    if os.path.isdir(watchDir) != True:
        print("Directory to monitor does not exist - " + watchDir)
        sys.exit()

    logger.info("Monitor started...")
    i = inotify.adapters.Inotify()

    i.add_watch(watchDir)

    try:
        for event in i.event_gen():
            if event is not None:
                (header, type_names, watch_path, filename) = event
                if type_names.count('IN_CLOSE_WRITE') == 1:
                    # file_name = filename.decode('utf-8')
                    # dir_name = watch_path.decode('utf-8')
                    file_name = filename
                    dir_name = watch_path
                    # print("File - " + dir_name + file_name + " " + str(type_names))
                    if file_name == "Stop.txt":
                        logger.info("Stopping monitor and logging")
                        i.remove_watch(watchDir)
                        disconnect_ws(ws)
                        logger.info("Monitor Stopped")
                        sys.exit()
                    elif file_name.startswith("sale") and "request" in file_name:
                        logger.info("Processing file - " +
                                    dir_name + file_name)
                        process_file(ws, dir_name + file_name)
                    else:
                        None

    except:
        disconnect_ws(ws)
        i.remove_watch(watchDir)


if __name__ == '__main__':
    watchDir = sys.argv[1]
    deviceID = sys.argv[2]
    print("WatchDir", watchDir)
    print("DeviceID", deviceID)
    if os.path.isdir(watchDir) != True:
        print("Directory to monitor does not exist - " + watchDir)
        sys.exit()
    baseDir = os.path.split(watchDir)
    baseDir = os.path.basename(baseDir[0])
    configure_logging(baseDir)
    logging.info("Connecting to FAPS Web Socket...")
    connect_ws()
    initialize_device(deviceID)
    _main(watchDir)
