import json
import requests
from sys import version_info
if (version_info > (3, 0)):
     # Import urljoin for Python 3
     from urllib.parse import urljoin
else:
     # Import urljoin for Python 2
     from urlparse import urljoin


class RestGateway:
    """
    | Last Revision: 6/23/2016
    | Version: 1.2.0
    | This class is required for all Python code making a call to REST API. Please refer to the gateway documentation web page for specifics on what parameters to use for each call.
    """
    def __init__(self, transactionData):
        self.version = "1.2.0"
        self.apiUrl = "https://secure-v.1stpaygateway.net/secure/RestGW/Gateway/Transaction/"
        # self.apiUrl = "https://secure-v.goemerchant.com/secure/RestGW/Gateway/Transaction/"
        # self.apiUrl = "https://secure.1stpaygateway.net/secure/RestGW/Gateway/Transaction/"
        self.TestMode = False
        self.data={}
        for key in transactionData:
            i = key
            self.data[i] = transactionData[i]
        self.status=str()
        self.result={}
        self.responsecode=""
        return

    def SwitchEnv(self):
        # Switch between production and validation
        if self.apiUrl == "https://secure.1stpaygateway.net/secure/RestGW/Gateway/Transaction/":
            self.apiUrl = "https://secure-v.1stpaygateway.net/secure/RestGW/Gateway/Transaction/"
            # self.apiUrl = "https://secure-v.goemerchant.com/secure/RestGW/Gateway/Transaction/"
            self.TestMode = True
        elif  self.apiUrl == "https://secure-v.1stpaygateway.net/secure/RestGW/Gateway/Transaction/":
        # elif self.apiUrl == "https://secure-v.goemerchant.com/secure/RestGW/Gateway/Transaction/":
            self.apiUrl = "https://secure.1stpaygateway.net/secure/RestGW/Gateway/Transaction/"
            self.TestMode = False
        else:
            self.apiUrl = "https://secure.1stpaygateway.net/secure/RestGW/Gateway/Transaction/"
            self.TestMode = False
        return True

    def performRequest(self):
        # Set self.status and self.result to empty so that it can store the new request
        self.status = str()
        self.result = {}
        self.responsedata = ""
        header = {'Content-Type': 'application/json', 'charset':'utf-8'}
        url = self.apiRequest
        postdata = dict(self.data)
        results = requests.post(url, data=json.dumps(postdata), headers=header)
        response = json.loads(results.text)
        self.responsecode = str(results.status_code)
        self.result = dict(response)
        # Set status according to the appropriate keys, guarding against unexpected return data
        if ('isSuccess' in self.result.keys() and self.result['isSuccess'] == True):
            self.status = "Success"
        elif ('validationHasFailed' in self.result.keys() and self.result['validationHasFailed'] == True):
            self.status = "Validation"
        elif ('isError' in self.result.keys() and self.result['isError'] == True):
            self.status = "Error"
        else:
            self.status = "Unknown"
        return self.result

    def createAuth(self):
        # print(self.apiUrl)
        self.apiRequest = urljoin(self.apiUrl,"Auth")
        return(RestGateway.performRequest(self))

    def createAuthUsing1stPayVault(self):
        self.apiRequest = urljoin(self.apiUrl,"AuthUsingVault")
        return(RestGateway.performRequest(self))

    def createSale(self):
        self.apiRequest = urljoin(self.apiUrl,"Sale")
        return(RestGateway.performRequest(self))

    def createSaleUsing1stPayVault(self):
        self.apiRequest = urljoin(self.apiUrl,"SaleUsingVault")
        return(RestGateway.performRequest(self))

    def createCredit(self):
        self.apiRequest = urljoin(self.apiUrl,"Credit")
        return(RestGateway.performRequest(self))

    def createCreditRetailOnly(self):
        self.apiRequest = urljoin(self.apiUrl,"CreditRetailOnly")
        return(RestGateway.performRequest(self))

    def createCreditRetailOnlyUsing1stPayVault(self):
        self.apiRequest = urljoin(self.apiUrl,"CreditRetailOnlyUsingVault")
        return(RestGateway.performRequest(self))

    def performVoid(self):
        self.apiRequest = urljoin(self.apiUrl,"Void")
        return(RestGateway.performRequest(self))

    def createReAuth(self):
        self.apiRequest = urljoin(self.apiUrl,"ReAuth")
        return(RestGateway.performRequest(self))

    def createReSale(self):
        self.apiRequest = urljoin(self.apiUrl,"ReSale")
        return(RestGateway.performRequest(self))

    def createReDebit(self):
        self.apiRequest = urljoin(self.apiUrl,"ReDebit")
        return(RestGateway.performRequest(self))

    def query(self):
        self.apiRequest = urljoin(self.apiUrl,"Query")
        return(RestGateway.performRequest(self))

    def closeBatch(self):
        self.apiRequest = urljoin(self.apiUrl,"CloseBatch")
        return(RestGateway.performRequest(self))

    def performSettle(self):
        self.apiRequest = urljoin(self.apiUrl,"Settle")
        return(RestGateway.performRequest(self))

    def applyTipAdjust(self):
        self.apiRequest = urljoin(self.apiUrl,"TipAdjust")
        return(RestGateway.performRequest(self))

    def performAchVoid(self):
        self.apiRequest = urljoin(self.apiUrl,"AchVoid")
        return(RestGateway.performRequest(self))

    def createAchCredit(self):
        self.apiRequest = urljoin(self.apiUrl,"AchCredit")
        return(RestGateway.performRequest(self))

    def createAchDebit(self):
        self.apiRequest = urljoin(self.apiUrl,"AchDebit")
        return(RestGateway.performRequest(self))

    def createAchCreditUsing1stPayVault(self):
        self.apiRequest = urljoin(self.apiUrl,"AchCreditUsingVault")
        return(RestGateway.performRequest(self))

    def createAchDebitUsing1stPayVault(self):
        self.apiRequest = urljoin(self.apiUrl,"AchDebitUsingVault")
        return(RestGateway.performRequest(self))

    def getAchCategories(self):
        self.apiRequest = urljoin(self.apiUrl,"AchGetCategories")
        return(RestGateway.performRequest(self))

    def createAchCategories(self):
         self.apiRequest = urljoin(self.apiUrl,"AchCreateCategory")
         return(RestGateway.performRequest(self))

    def deleteAchCategories(self):
         self.apiRequest = urljoin(self.apiUrl,"AchDeleteCategory")
         return(RestGateway.performRequest(self))

    def setupAchStore(self):
         self.apiRequest = urljoin(self.apiUrl,"AchSetupStore")
         return(RestGateway.performRequest(self))

    def createVaultContainer(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultCreateContainer")
        return(RestGateway.performRequest(self))

    def createVaultAchRecord(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultCreateAchRecord")
        return(RestGateway.performRequest(self))

    def createVaultCreditCardRecord(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultCreateCCRecord")
        return(RestGateway.performRequest(self))

    def createVaultShippingRecord(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultCreateShippingRecord")
        return(RestGateway.performRequest(self))

    def deleteVaultContainerAndAllAsscData(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultDeleteContainerAndAllAsscData")
        return(RestGateway.performRequest(self))

    def deleteVaultAchRecord(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultDeleteAchRecord")
        return(RestGateway.performRequest(self))

    def deleteVaultCreditCardRecord(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultDeleteCCRecord")
        return(RestGateway.performRequest(self))

    def deleteVaultShippingRecord(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultDeleteShippingRecord")
        return(RestGateway.performRequest(self))

    def updateVaultContainer(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultUpdateContainer")
        return(RestGateway.performRequest(self))

    def updateVaultAchRecord(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultUpdateAchRecord")
        return(RestGateway.performRequest(self))

    def updateVaultCreditCardRecord(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultUpdateCCRecord")
        return(RestGateway.performRequest(self))

    def updateVaultShippingRecord(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultUpdateShippingRecord")
        return(RestGateway.performRequest(self))

    def queryVaults(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultQueryVault")
        return(RestGateway.performRequest(self))

    def queryVaultForCreditCardRecords(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultQueryCCRecord")
        return(RestGateway.performRequest(self))

    def queryVaultForAchRecords(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultQueryAchRecord")
        return(RestGateway.performRequest(self))

    def queryVaultForShippingRecords(self):
        self.apiRequest = urljoin(self.apiUrl,"VaultQueryShippingRecord")
        return(RestGateway.performRequest(self))

    def modifyRecurring(self):
        self.apiRequest = urljoin(self.apiUrl,"RecurringModify")
        return(RestGateway.performRequest(self))

    def submitAcctUpdater(self):
        self.apiRequest = urljoin(self.apiUrl,"AccountUpdaterSubmit")
        return(RestGateway.performRequest(self))

    def submitAcctUpdaterVault(self):
        self.apiRequest = urljoin(self.apiUrl,"AccountUpdaterSubmitVault")
        return(RestGateway.performRequest(self))

    def getAcctUpdaterReturn(self):
        self.apiRequest = urljoin(self.apiUrl,"AccountUpdaterReturn")
        return(RestGateway.performRequest(self))

