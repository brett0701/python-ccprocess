import sys
import os
import json
import ast
import gateway
import MerchantInfo


def process_file(jsonfile):
    global responseFile
    responseFile = jsonfile.replace("request", "response")
    json_data = {}
    try:
        file = open(jsonfile, "r")
        lines = file.readlines()
        if lines[0].strip() == "VOID":
            transType = "VOID"
            json_data['merchantKey'] = lines[1].strip()
            json_data['processorId'] = lines[2].strip()
            json_data['refNumber'] = lines[3].strip()
            # json_data['transactionAmount'] = lines[4].strip()
            # print(json_data)
        if lines[0].strip() == "SALE":
            transType = "SALE"
            json_data['merchantKey'] = lines[1].strip()
            json_data['processorId'] = lines[2].strip()
            json_data['cardNumber'] = lines[3].strip()
            json_data['cardExpMonth'] = lines[4].strip()
            json_data['cardExpYear'] = lines[5].strip()
            json_data['cVV'] = lines[6].strip()
            json_data['creditCardToken'] = lines[7].strip()
            json_data['transactionAmount'] = lines[8].strip()
            json_data['preventPartial'] = "1"
            # print(json_data)
        if lines[0].strip() == "AUTH":
            transType = "AUTH"
            json_data['merchantKey'] = lines[1].strip()
            json_data['processorId'] = lines[2].strip()
            json_data['cardNumber'] = lines[3].strip()
            json_data['cardExpMonth'] = lines[4].strip()
            json_data['cardExpYear'] = lines[5].strip()
            json_data['cVV'] = lines[6].strip()
            json_data['creditCardToken'] = lines[7].strip()
            json_data['transactionAmount'] = lines[8].strip()
            json_data['preventPartial'] = "1"
            # print(json_data)
        if lines[0].strip() == "REFUND":
            transType = "REFUND"
            json_data['merchantKey'] = lines[1].strip()
            json_data['processorId'] = lines[2].strip()
            json_data['refNumber'] = lines[3].strip()
            json_data['transactionAmount'] = lines[4].strip()
            # print(json_data)
        if lines[0].strip() == "SETTLE":
            transType = "SETTLE"
            json_data['merchantKey'] = lines[1].strip()
            json_data['processorId'] = lines[2].strip()
            # json_data['creditCardToken'] = lines[3].strip()
            json_data['refNumber'] = lines[3].strip()
            json_data['transactionAmount'] = lines[4].strip()
            # print(json_data)
        file.close()
    except IndexError as e:
        f = open(responseFile, "w")
        f.write("Error: Incorrect amount of parameters in request file")
        f.close()
        sys.exit()
    except IOError as e:
        f = open(responseFile, "w")
        f.write("I/O error({0}): {1} {2}".format(e.errno,
                                                 e.strerror, jsonfile))
        f.close()
        sys.exit()
    except:
        f = open(responseFile, "w")
        f.write("Unexepected error:", sys.exc_info()[0])
        f.close()
        sys.exit()
    process_data(json_data, transType)


def process_data(data, transType):
    gwcall = gateway.RestGateway(data)
    if transType == "VOID":
        gwcall.performVoid()

    if transType == "REFUND":
        gwcall.createCredit()

    if transType == "SALE":
        gwcall.createSale()

    if transType == "AUTH":
        gwcall.createAuth()

    if transType == "SETTLE":
        gwcall.performSettle()

    if gwcall.status == 'Success':
        return success(gwcall, transType)
    if gwcall.status == 'Validation':
        return errors_and_validation(gwcall)
    if gwcall.status == 'Error':
        return errors_and_validation(gwcall)

##########################################################
#      SUCCESS HANDLER
##########################################################


def success(result, transType):
    # print('Success!')
    # print(transType)
    # print(result.result)
    f = open(responseFile, "w")
    if transType == "SALE":
        partialAuth = "No"
        if result.result['data']['isPartial']:
            partialAuth = "Yes"
        f.write("Error: \n")
        f.write("Approval Code: " + result.result['data']['authCode'] + "\n")
        f.write("Partial Auth: " + partialAuth + "\n")
        f.write("Auth Amount: " +
                str(result.result['data']['partialAmountApproved']) + "\n")
        f.write("Reference #: " +
                result.result['data']['referenceNumber'] + "\n")
        f.write("Token: " + result.result['data']['token'] + "\n")
        f.write("Order ID: " + result.result['data']['orderId'] + "\n")
        f.write("Auth Response: " +
                result.result['data']['authResponse'] + "\n")
    if transType == "AUTH":
        partialAuth = "No"
        if result.result['data']['isPartial']:
            partialAuth = "Yes"
        f.write("Error: \n")
        f.write("Approval Code: " + result.result['data']['authCode'] + "\n")
        f.write("Partial Auth: " + partialAuth + "\n")
        f.write("Auth Amount: " +
                str(result.result['data']['partialAmountApproved']) + "\n")
        f.write("Reference #: " +
                result.result['data']['referenceNumber'] + "\n")
        f.write("Token: " + result.result['data']['token'] + "\n")
        f.write("Order ID: " + result.result['data']['orderId'] + "\n")
        f.write("Auth Response: " +
                result.result['data']['authResponse'] + "\n")
    if transType == "VOID":
        f.write("Error: \n")
        f.write("Auth Response: " +
                result.result['data']['authResponse'] + "\n")
        # f.write("Parent Reference #: " + result.result['data']['parentReferenceNumber'] + "\n")
        f.write("Reference #: " +
                result.result['data']['referenceNumber'] + "\n")
    if transType == "REFUND":
        f.write("Error: \n")
        f.write("Auth Response: " +
                result.result['data']['authResponse'] + "\n")
        f.write("Reference #: " +
                result.result['data']['referenceNumber'] + "\n")
        f.write("Credit Amount: " +
                result.result['data']['creditAmount'] + "\n")
    if transType == "SETTLE":
        f.write("Error: \n")
        f.write("Batch #: " + result.result['data']['batchNumber'] + "\n")
        f.write("Auth Response: " +
                result.result['data']['authResponse'] + "\n")
        f.write("Reference #: " +
                result.result['data']['referenceNumber'] + "\n")
        f.write("Settle Amount: " +
                result.result['data']['settleAmount'] + "\n")
    f.close()
    return

##########################################################
#      VALIDATION AND ERROR HANDLER
##########################################################


def errors_and_validation(result):
    if result.status == 'Validation':
        validationErr = ''
        keyList = []
        index = 0
        # print("Please correct the following errors: ",'\n')
        for i in result.result['validationFailures']:
            for key in i:
                if key == "key":
                    # Insert key into keyList so that we have a clear list of the fields with validation errors
                    keyList.insert(index, i[key])
                    index += 1
                if key == "message":
                    validationErr = validationErr + i[key]
                    # print(i[key],'\n')
        if validationErr != '':
            f = open(responseFile, "w")
            f.write("Error: " + validationErr + "\n")
            f.close()
    # Allow user to re-process transaction
    # Perform any additional tasks if you need to
    elif result.status == 'Error':
        # print(result.result)
        # print("There was an error processing your request. \n")
        # print("Errors: \n")
        # print(result.result['errorMessages'])
        errorMsg = ''
        for errorResponse in result.result['errorMessages']:
            errorMsg = errorMsg + errorResponse
        f = open(responseFile, "w")
        if 'authCode' in result.result['data']:
            f.write("Error: " + result.result['data']['authCode'] + "\n")
        else:
            f.write("Error: " + errorMsg + "\n")
        f.close()
    return


if __name__ == '__main__':
    jsonfile = sys.argv[1]
    process_file(jsonfile)
