import sys
import os
import json
import ast
import gateway
import MerchantInfo


def run_query():
    if 'queryStartMonth' not in data:
        data['queryStartMonth'] = input(
            'Please specify start month for search: ')
    if 'queryStartDay' not in data:
        data['queryStartDay'] = input('Please specify start day for search: ')
    if 'queryStartYear' not in data:
        data['queryStartYear'] = input(
            'Please specify start year for search (default 2015): ')
    if 'queryEndMonth' not in data:
        data['queryEndMonth'] = input('Please specify end month for search: ')
    if 'queryEndDay' not in data:
        data['queryEndDay'] = input('Please specify end day for search: ')
    if 'queryEndYear' not in data:
        data['queryEndYear'] = input(
            'Please specify end year for search (default 2015): ')
    process_data(data, "Query")


def process_data(data, transType):
    gwcall = gateway.RestGateway(data)
    if transType == "Query":
        gwcall.query()

    if gwcall.status == 'Success':
        return success(gwcall, "Query")
    if gwcall.status == 'Validation':
        return errors_and_validation(gwcall)
    if gwcall.status == 'Error':
        return errors_and_validation(gwcall)

##########################################################
#      SUCCESS HANDLER
##########################################################


def success(result, transType):
    print('Success!')
    print(transType)
    # print(result.result)
    print('OrderID  Reference# AuthResponse    TransDate   Amount OrigAmount TransType \n')
    print('-------- ---------- --------------- ----------- ------ ---------- ---------  \n')
    try:
        for index, element in enumerate(result.result):
            print(result.result['data']['orders']
                  [index]['orderInfo']['orderId'], end='')
            print(' ', end=''),
            print(result.result['data']['orders']
                  [index]['referenceNumber'], end=''),
            print('  ', end=''),
            print(result.result['data']['orders']
                  [index]['orderInfo']['authResponse'], end=''),
            if len(result.result['data']['orders'][index]['orderInfo']['authResponse']) == 13:
                print('   ', end=''),
            else:
                print('        ', end=''),
            print(result.result['data']['orders'][index]
                  ['orderInfo']['transactionDate'], end=''),
            print('   ', end=''),
            print(result.result['data']['orders']
                  [index]['orderInfo']['amount'], end=''),
            print('     ', end=''),
            print(result.result['data']['orders'][index]
                  ['orderInfo']['originalAmount'], end=''),
            print('        ', end=''),
            print(result.result['data']['orders'][index]
                  ['orderInfo']['transactionType'], end='')
            print('')
    except IndexError:
        pass
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
        # print("There was an error processing your request. \n")
        # print("Errors: \n")
        # print(result.result['errorMessages'])
        errorMsg = ''
        for errorResponse in result.result['errorMessages']:
            errorMsg = errorMsg + errorResponse
        f = open(responseFile, "w")
        f.write("Error: " + errorMsg + "\n")
        f.close()
    return


if __name__ == '__main__':
    data = dict(MerchantInfo.merchant)
    data['processorId'] = '206498'
    data['queryTransType'] = ''
    data['queryStartYear'] = '2019'
    data['queryEndYear'] = '2019'
    run_query()
