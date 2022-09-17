# from asyncio.windows_events import None
from email import message
import json
from locale import currency
import re
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
# from django.http import FileResponse
# import io
# from reportlab.pdfgen import canvas
# from reportlab.lib.units import inch
# from reportlab.lib.pagesizes import letter
from .models import Cart, CustomerReceipt, CreditReceipt, QuotationReceipt, Account, Customer, Payable,Stock, Transfer,Vendor,Cheques, CashInvoice,PurchaseOrder
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Sum
from currencies.models import Currency
from django.db.models import Count, F
from datetime import datetime
import random
def get_code():
    code = random.randint(1000000, 9999999)
    return code

def get_time():
    now = datetime.now().strftime("%Y-%m-%d")
    return now

def get_cookie(request):
    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    # ip = request.META.get('REMOTE_ADDR')
    x_forwarded_for = request.META.get('HTTP_COOKIE') if 'HTTP_COOKIE' in request.META else ''
    if x_forwarded_for != '':
        stip = x_forwarded_for.split(';')[0]
        ip = stip.split('=')[1]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Create your views here.
def profitReport(request):
    myDate = datetime.now()

    labels = []
    data = []

    if "plotChart" in request.POST:    
        datestart = request.POST["start_date"]
        dateend = request.POST["end_date"] 
        # annotate(distance=ExpressionWrapper(
        stocks = Stock.objects.values('inventoryPart').annotate(percentageProfit=F('percentageProfit')).order_by('inventoryPart').filter(created_at__lte=dateend,created_at__gte=datestart)
    else:
        stocks = Stock.objects.values('inventoryPart').annotate(percentageProfit=F('percentageProfit')).order_by('inventoryPart').filter(created_at__lte=myDate.strftime("%Y-%m-%d"))

    # Chart data
    
    for stockData in stocks:
        labels.append(stockData['inventoryPart'])
    
    
    for stockData in stocks:
        data.append(stockData['percentageProfit'])

    
    context ={'labels': labels,
              'data': data,
    }
    return render(request,'profitReport.html',context)

@login_required
def cartReceipt(request):
    curry = Currency.objects.filter(code='USD')
    currency = request.session['currency']
    for currr in curry:
        curr = currr.factor
    ct_array =  Cart.objects.filter(status=0, receiptNumber=get_cookie(request))
    if request.method == 'POST':
        try:
            amount = request.POST.get('total')
            discount = request.POST.get('discount')
            receiptNumber = get_code()
            customerName = request.POST.get('customerName')
            modeOfPayment= request.POST.get('method')
            pay_type = request.POST.get('payType')
            for t in ct_array:
                if modeOfPayment != "Quotation":
                    Stock.objects.filter(inventoryPart=str(t.item_purchased)).update(piecesQuantity=F('piecesQuantity')-t.quantity)
                Cart.objects.filter(item_purchased=t.item_purchased,status=0).update(status=1, receiptNumber=receiptNumber, type=modeOfPayment)
            item_purchased =''
            quantity = 1
            price = 1
            purchasedFrom= request.POST.get('purchasedFrom')
            date= get_time()
            if modeOfPayment == 'Cash':
                CustomerReceipt.objects.create(
                receiptNumber=receiptNumber,
                customerName=customerName,
                modeOfPayment=modeOfPayment,
                item_purchased=item_purchased,
                purchasedFrom=purchasedFrom,
                quantity=quantity,
                price=price,
                discount=discount,
                totalAmountPaid=amount,
                currency=currency,
                date=date,
                payType=pay_type
                )
                Account.objects.filter(name='SJ & Firdous').update(cashFromReceipts=F('cashFromReceipts') + float(amount))
            elif modeOfPayment == 'Credit':
                CreditReceipt.objects.create(
                    creditNumber=receiptNumber,
                    customerName=customerName,
                    modeOfPayment=modeOfPayment,
                    item_purchased=item_purchased,
                    purchasedFrom=purchasedFrom,
                    quantity=quantity,
                    price=price,
                    discount=discount,
                    totalAmountPaid=amount,
                    currency=currency,
                    date=date,
                    payType=pay_type
                    )
                Account.objects.filter(name='SJ & Firdous').update(debtorBalance=F('debtorBalance') + float(amount))
            elif modeOfPayment == 'Quotation':
                QuotationReceipt.objects.create(
                    quotationNumber=receiptNumber,
                    customerName=customerName,
                    modeOfPayment=modeOfPayment,
                    item_purchased=item_purchased,
                    purchasedFrom=purchasedFrom,
                    quantity=quantity,
                    price=price,
                    discount=discount,
                    totalAmountPaid=amount,
                    currency=currency,
                    date=date,
                    payType=pay_type
                )
            return redirect("preview-receipt", receipt=receiptNumber)
        except CustomerReceipt.DoesNotExist:
            return HttpResponse('Fail') 

@login_required
def dashboard(request):

    myDate = datetime.now()

    labels = []
    data = []

    if "plotChart" in request.POST:    
        datestart = request.POST["start_date"]
        dateend = request.POST["end_date"] 
        # annotate(distance=ExpressionWrapper(
        customers = Customer.objects.values('item_purchased__inventoryPart').annotate(mycount=F('quantity')*Count('item_purchased')).order_by('item_purchased').filter(date__lte=dateend,date__gte=datestart)
    else:
        customers = Customer.objects.values('item_purchased__inventoryPart').annotate(mycount=F('quantity')*Count('item_purchased')).order_by('item_purchased').filter(date__lte=myDate.strftime("%Y-%m-%d"))

    # Chart data

    print("------here--------")
    print(customers)
    
    for stockData in customers:
        labels.append(stockData['item_purchased__inventoryPart'])
    
    
    for stockData in customers:
        data.append(stockData['mycount'])

    
    context ={'labels': labels,
              'data': data,
    }
    return render(request,'dashboard.html',context)


@login_required
def index(request):

    defaultcurr = settings.DEFAULT_CURRENCY
    request.session['cookie'] = ''
    if not request.session.has_key('currency'):
        request.session['currency'] = settings.DEFAULT_CURRENCY
    
    labels = []
    data = []

    if request.user.is_staff:
        customers = Customer.objects.all()
        stocks = Stock.objects.all()
        vendorsPaid = Transfer.objects.all()
        customercount = Customer.objects.all().count()
        stockscount = Stock.objects.all().count()
        vendorcount = Vendor.objects.all().count()
        context ={'customers':customers,
              'customercount':customercount,
              'stockscount':stockscount,
              'vendorcount':vendorcount,
              'stocks':stocks
              
              }
    # customers = Customer.objects.filter(addedby=request.user)
    customers = Customer.objects.all()
    # print(customers)
    vendorsPaid = Transfer.objects.all()
    stocks = Stock.objects.all()
    customerCash = Customer.objects.filter(modeOfPayment='Cash')
    customerBank = Customer.objects.filter(modeOfPayment='Bank')
    customerDebtors = Customer.objects.filter(order_status='Pending').count()
    expenses = Cheques.objects.all()


    # Chart data
    for custData in customers:
        labels.append(custData.modeOfPayment)
    for custDataCash in customerCash:
        data.append(custDataCash.totalAmountPaid)
    for custDataBank in customerBank:
        data.append(custDataBank.totalAmountPaid)

    #new math 
    newCustCashTotal = Customer.objects.filter(modeOfPayment='Cash').aggregate(Sum('totalAmountPaid'))['totalAmountPaid__sum']
    newCustBankTotal = Customer.objects.filter(modeOfPayment='Bank').aggregate(Sum('totalAmountPaid'))['totalAmountPaid__sum']
    newVendorPaidinCashTotal = Transfer.objects.filter(modeOfPayment='Cash').aggregate(Sum('amountPaid'))['amountPaid__sum']
    newVendorPaidinBankTotal = Transfer.objects.filter(modeOfPayment='Bank').aggregate(Sum('amountPaid'))['amountPaid__sum']
    expenseTotal = Cheques.objects.aggregate(Sum('totalAmountPaid'))['totalAmountPaid__sum']
    debtorBalanceTotal = Customer.objects.aggregate(Sum('balance'))['balance__sum']
    
    if newVendorPaidinBankTotal is not None:
        accountBalance = ((newCustCashTotal-newVendorPaidinCashTotal) + (newCustBankTotal-newVendorPaidinBankTotal)) - expenseTotal 
        grandTotal = (newCustCashTotal-newVendorPaidinCashTotal) + (newCustBankTotal-newVendorPaidinBankTotal) 
    else:
        accountBalance = ((newCustCashTotal-newVendorPaidinCashTotal) + newCustBankTotal) - expenseTotal 
        grandTotal = (newCustCashTotal-newVendorPaidinCashTotal) + newCustBankTotal
    
     
    try:
        acc = Account.objects.get(name='SJ & Firdous')
        if newVendorPaidinCashTotal is None:
            acc.cashAccount = newCustCashTotal
            acc.bankAccount = newCustBankTotal
            acc.expensesTotal = expenseTotal
            acc.debtorBalance = debtorBalanceTotal
            acc.accountBalance = (newCustCashTotal+newCustBankTotal) - expenseTotal
            acc.grandTotal = acc.cashFromReceipts+newCustCashTotal + newCustBankTotal
            acc.save()
            
        elif newVendorPaidinBankTotal is None:
            acc.cashAccount = newCustCashTotal - newVendorPaidinCashTotal
            acc.bankAccount = newCustBankTotal
            acc.expensesTotal = expenseTotal
            acc.debtorBalance = debtorBalanceTotal
            acc.accountBalance = (( newCustCashTotal - newVendorPaidinCashTotal ) + newCustBankTotal) - expenseTotal
            acc.grandTotal = (newCustCashTotal - newVendorPaidinCashTotal) + acc.cashFromReceipts+ newCustBankTotal
            
            acc.save()
        else:
            acc.cashAccount = newCustCashTotal - newVendorPaidinCashTotal
            acc.bankAccount = newCustBankTotal - newVendorPaidinBankTotal
            acc.expensesTotal = expenseTotal
            acc.debtorBalance = debtorBalanceTotal
            acc.accountBalance = accountBalance
            acc.grandTotal = acc.cashFromReceipts + grandTotal
            acc.save()
    except Account.DoesNotExist:
        acc = Account(name='SJ & Firdous')
        if newVendorPaidinCashTotal is None and  newVendorPaidinBankTotal is None:
            acc.cashAccount = newCustCashTotal
            acc.bankAccount = newCustBankTotal
            acc.expensesTotal = expenseTotal
            acc.debtorBalance = debtorBalanceTotal
            acc.accountBalance = (newCustCashTotal+newCustBankTotal) - expenseTotal
            acc.grandTotal = acc.cashFromReceipts + newCustCashTotal + newCustBankTotal
            acc.save()
            
        elif newVendorPaidinBankTotal is None:
            acc.cashAccount = newCustCashTotal - newVendorPaidinCashTotal
            acc.bankAccount = newCustBankTotal
            acc.expensesTotal = expenseTotal
            acc.debtorBalance = debtorBalanceTotal
            acc.accountBalance = (( newCustCashTotal - newVendorPaidinCashTotal ) + newCustBankTotal) - expenseTotal
            acc.grandTotal = (newCustCashTotal - newVendorPaidinCashTotal) + acc.cashFromReceipts + newCustBankTotal
            acc.save()

        elif newVendorPaidinCashTotal is None:
            acc.cashAccount = newCustCashTotal
            acc.bankAccount = newCustBankTotal - newVendorPaidinBankTotal
            acc.expensesTotal = expenseTotal
            acc.debtorBalance = debtorBalanceTotal
            acc.accountBalance = (newCustCashTotal + (newCustBankTotal - newVendorPaidinBankTotal)) - expenseTotal
            acc.grandTotal = newCustCashTotal + acc.cashFromReceipts + (newCustBankTotal - newVendorPaidinBankTotal)
            acc.save()

        else:
            acc.cashAccount = newCustCashTotal - newVendorPaidinCashTotal
            acc.bankAccount = newCustBankTotal - newVendorPaidinBankTotal
            acc.expensesTotal = expenseTotal
            acc.debtorBalance = debtorBalanceTotal
            acc.accountBalance = accountBalance
            acc.grandTotal = acc.cashFromReceipts + grandTotal
            acc.save()

    
    
    
    
    for stockProfit in stocks:
        percstockProfit = (stockProfit.sellingPrice - stockProfit.costPrice) * 100

    customercount = Customer.objects.all().count()
    stockscount = Stock.objects.all().count()
    vendorcount = Vendor.objects.all().count()
    accounts = Account.objects.filter(name='SJ & Firdous').order_by('-id')[0]

    # grandtotal = cash + bank
    # request.session['cash']=cash

    # accountBalance = grandtotal - expensesTotal
    
    
    
    context ={'customers':customers,
              'customercount':customercount,
              'stockscount':stockscount,
              'vendorcount':vendorcount,
              'grandtotal':accounts.grandTotal,
              'percstockProfit':percstockProfit,
              'cash':accounts.cashAccount,
              'bank':accounts.bankAccount,
              'expensesTotal':accounts.expensesTotal,
              'customerDebtors':customerDebtors,
              'debtorBal':accounts.debtorBalance,
              'accoutnBalance': accounts.accountBalance,
              'cashfromreceipts':accounts.cashFromReceipts,
              'labels': labels,
              'data': data,
              'stocks':stocks
              }
    
    for stock in stocks:
        if request.user.is_staff and stock.piecesQuantity < 1 :
            messages.warning(request, stock.inventoryPart+' are running low in stock Please add more!!')
            return render(request, 'index.html', context)
    
    for customer in customers:
        if customer.is_past_due and customer.due_date != None:
            messages.warning(request, customer.customerName+'\'s due date of '+customer.due_date.strftime("%Y-%m-%d")+ ' is past, please follow up and update!!')
            return render(request, 'index.html', context)
        
    return render(request,'index.html',context)

# New
def customerReceipt(request):
    curry = Currency.objects.filter(code='SSP')
    for currr in curry:
        curr = currr.factor
    stocks = Stock.objects.all()
    if request.method == 'POST':
        if 'sender' in request.POST:
            
            try:
                receiptNumber = request.POST.get('chequeNo')
                customerName= request.POST.get('customerName')
                modeOfPayment= request.POST.get('modeOfPayment')
                item_purchased= request.POST.get('ice-cream-choice1')+"--"+request.POST.get('ice-cream-choice2')+"--"+request.POST.get('ice-cream-choice3')+"--"+request.POST.get('ice-cream-choice4')+request.POST.get('ice-cream-choice5')
                # item = get_object_or_404(Stock, inventoryPart=item_purchased)
                purchasedFrom= request.POST.get('purchasedFrom')
                quantity= request.POST.get('quantity1')+"--"+request.POST.get('quantity2')+"--"+request.POST.get('quantity3')+"--"+request.POST.get('quantity4')+"--"+request.POST.get('quantity5')
                price= request.POST.get('price1')+"--"+request.POST.get('price2')+"--"+request.POST.get('price3')+"--"+request.POST.get('price4')+"--"+request.POST.get('price5')
                discount= request.POST.get('discount')
                
                gtt = request.POST.get('GTT')
                
                # Get the total and send it to the cash account
                totalAmountPaid= request.POST.get('totalAmountPaid1')+"--"+request.POST.get('totalAmountPaid2')+"--"+request.POST.get('totalAmountPaid3')+"--"+request.POST.get('totalAmountPaid4')+"--"+request.POST.get('totalAmountPaid5')
                date= request.POST.get('date')
                
                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice1'))).update(piecesQuantity=F('piecesQuantity')-request.POST.get('quantity1'))
                
                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice2'))).update(piecesQuantity=F('piecesQuantity')-request.POST.get('quantity2'))
                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice3'))).update(piecesQuantity=F('piecesQuantity')-request.POST.get('quantity3'))
                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice4'))).update(piecesQuantity=F('piecesQuantity')-request.POST.get('quantity4'))
                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice5'))).update(piecesQuantity=F('piecesQuantity')-request.POST.get('quantity5'))

                CustomerReceipt.objects.create(
                    receiptNumber=receiptNumber,
                    customerName=customerName,
                    modeOfPayment=modeOfPayment,
                    item_purchased=item_purchased,
                    purchasedFrom=purchasedFrom,
                    quantity=quantity,
                    price=price,
                    discount=discount,
                    totalAmountPaid=totalAmountPaid,
                    date=date,
                    )

                # This below gets the cash inserted and adds it onto the cash from receipts
                currencyy = request.POST.get('usdd')
                print(currencyy)
                if currencyy == "usd":
                    curryr = Currency.objects.filter(code='SSP')
                    for currr in curryr:
                        curr = currr.factor
                    usd2ssp = float(gtt) * float(curr)
                    Account.objects.filter(name='SJ & Firdous').update(cashFromReceipts=F('cashFromReceipts') + float(usd2ssp))

                Account.objects.filter(name='SJ & Firdous').update(cashFromReceipts=F('cashFromReceipts') + float(gtt))

                print("Added the total amount from receipts to cashFromReceipts account")

            except CustomerReceipt.DoesNotExist:
                return HttpResponse('Fail') 
    context = {
        'loopdata': [1,2,3,4,5],
        'stocks':stocks,
        'curr':curr,
        }
    return render(request,'customerReceipt.html',context)

# Quotation(Proforma)
def proformaReceipt(request):
    curry = Currency.objects.filter(code='SSP')
    for currr in curry:
        curr = currr.factor
    stocks = Stock.objects.all()
    if request.method == 'POST':
        if 'sender' in request.POST:

            try:
                quotationNumber = request.POST.get('chequeNo')
                customerName = request.POST.get('customerName')
                modeOfPayment = request.POST.get('modeOfPayment')
                item_purchased = request.POST.get('ice-cream-choice1') + "--" + request.POST.get(
                    'ice-cream-choice2') + "--" + request.POST.get('ice-cream-choice3') + "--" + request.POST.get(
                    'ice-cream-choice4') + request.POST.get('ice-cream-choice5')
                # item = get_object_or_404(Stock, inventoryPart=item_purchased)
                purchasedFrom = request.POST.get('purchasedFrom')
                quantity = request.POST.get('quantity1') + "--" + request.POST.get(
                    'quantity2') + "--" + request.POST.get('quantity3') + "--" + request.POST.get(
                    'quantity4') + "--" + request.POST.get('quantity5')
                price = request.POST.get('price1') + "--" + request.POST.get('price2') + "--" + request.POST.get(
                    'price3') + "--" + request.POST.get('price4') + "--" + request.POST.get('price5')
                discount = request.POST.get('discount1') + "--" + request.POST.get(
                    'discount2') + "--" + request.POST.get('discount3') + "--" + request.POST.get(
                    'discount4') + "--" + request.POST.get('discount5')

                gtt = request.POST.get('GTT')
                # I DONT NEED THIS IN QUOTATION RECCEIPT
                # Get the total and send it to the cash account
                totalAmountPaid = request.POST.get('totalAmountPaid1') + "--" + request.POST.get(
                    'totalAmountPaid2') + "--" + request.POST.get('totalAmountPaid3') + "--" + request.POST.get(
                    'totalAmountPaid4') + "--" + request.POST.get('totalAmountPaid5')
                date = request.POST.get('date')

                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice1'))).update(
                    piecesQuantity=F('piecesQuantity') - request.POST.get('quantity1'))
                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice2'))).update(
                    piecesQuantity=F('piecesQuantity') - request.POST.get('quantity2'))
                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice3'))).update(
                    piecesQuantity=F('piecesQuantity') - request.POST.get('quantity3'))
                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice4'))).update(
                    piecesQuantity=F('piecesQuantity') - request.POST.get('quantity4'))
                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice5'))).update(
                    piecesQuantity=F('piecesQuantity') - request.POST.get('quantity5'))

                QuotationReceipt.objects.create(
                    quotationNumber=quotationNumber,
                    customerName=customerName,
                    modeOfPayment=modeOfPayment,
                    item_purchased=item_purchased,
                    purchasedFrom=purchasedFrom,
                    quantity=quantity,
                    price=price,
                    discount=discount,
                    totalAmountPaid=totalAmountPaid,
                    date=date,
                )
                # # i dont need this too
                # # This below gets the cash inserted and adds it onto the cash from receipts
                # currencyy = request.POST.get('usdd')
                # print(currencyy)
                # if currencyy == "usd":
                #     curryr = Currency.objects.filter(code='SSP')
                #     for currr in curryr:
                #         curr = currr.factor
                #     usd2ssp = float(gtt) * float(curr)
                #     Account.objects.filter(name='SJ & Firdous').update(
                #         cashFromReceipts=F('cashFromReceipts') + float(usd2ssp))
                #
                # Account.objects.filter(name='SJ & Firdous').update(cashFromReceipts=F('cashFromReceipts') + float(gtt))
                #
                # print("Added the total amount from receipts to cashFromReceipts account")

            except QuotationReceipt.DoesNotExist:
                return HttpResponse('Fail')
    context = {
        'loopdata': [1, 2, 3, 4, 5],
        'stocks': stocks,
        'curr': curr,
    }
    return render(request, 'quotationReceipt.html', context)

# Credit Receipt
def creditReceipt(request):
    curry = Currency.objects.filter(code='SSP')
    for currr in curry:
        curr = currr.factor
    stocks = Stock.objects.all()
    if request.method == 'POST':
        if 'sender' in request.POST:

            try:
                creditNumber = request.POST.get('chequeNo')
                customerName = request.POST.get('customerName')
                modeOfPayment = request.POST.get('modeOfPayment')
                item_purchased = request.POST.get('ice-cream-choice1') + "--" + request.POST.get(
                    'ice-cream-choice2') + "--" + request.POST.get('ice-cream-choice3') + "--" + request.POST.get(
                    'ice-cream-choice4') + request.POST.get('ice-cream-choice5')
                # item = get_object_or_404(Stock, inventoryPart=item_purchased)
                purchasedFrom = request.POST.get('purchasedFrom')
                quantity = request.POST.get('quantity1') + "--" + request.POST.get(
                    'quantity2') + "--" + request.POST.get('quantity3') + "--" + request.POST.get(
                    'quantity4') + "--" + request.POST.get('quantity5')
                price = request.POST.get('price1') + "--" + request.POST.get('price2') + "--" + request.POST.get(
                    'price3') + "--" + request.POST.get('price4') + "--" + request.POST.get('price5')
                discount = request.POST.get('discount1') + "--" + request.POST.get(
                    'discount2') + "--" + request.POST.get('discount3') + "--" + request.POST.get(
                    'discount4') + "--" + request.POST.get('discount5')

                gtt = request.POST.get('GTT')
                # I want this to be added to receivable account(debtorbalance account)
                # Get the total and send it to the receivable coz these are guys who have taken good on credit
                totalAmountPaid = request.POST.get('totalAmountPaid1') + "--" + request.POST.get(
                    'totalAmountPaid2') + "--" + request.POST.get('totalAmountPaid3') + "--" + request.POST.get(
                    'totalAmountPaid4') + "--" + request.POST.get('totalAmountPaid5')
                date = request.POST.get('date')

                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice1'))).update(
                    piecesQuantity=F('piecesQuantity') - request.POST.get('quantity1'))
                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice2'))).update(
                    piecesQuantity=F('piecesQuantity') - request.POST.get('quantity2'))
                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice3'))).update(
                    piecesQuantity=F('piecesQuantity') - request.POST.get('quantity3'))
                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice4'))).update(
                    piecesQuantity=F('piecesQuantity') - request.POST.get('quantity4'))
                Stock.objects.filter(inventoryPart=str(request.POST.get('ice-cream-choice5'))).update(
                    piecesQuantity=F('piecesQuantity') - request.POST.get('quantity5'))

                CreditReceipt.objects.create(
                    creditNumber=creditNumber,
                    customerName=customerName,
                    modeOfPayment=modeOfPayment,
                    item_purchased=item_purchased,
                    purchasedFrom=purchasedFrom,
                    quantity=quantity,
                    price=price,
                    discount=discount,
                    totalAmountPaid=totalAmountPaid,
                    date=date,
                )
                # This below gets the cash inserted and adds it onto the cash from receipts
                currencyy = request.POST.get('usdd')
                print(currencyy)
                if currencyy == "usd":
                    curryr = Currency.objects.filter(code='SSP')
                    for currr in curryr:
                        curr = currr.factor
                    usd2ssp = float(gtt) * float(curr)
                    Account.objects.filter(name='SJ & Firdous').update(
                        debtorBalance=F('debtorBalance') + float(usd2ssp))

                Account.objects.filter(name='SJ & Firdous').update(debtorBalance=F('debtorBalance') + float(gtt))

                print("Added the total amount from receipts to cashFromReceipts account")

            except CreditReceipt.DoesNotExist:
                return HttpResponse('Fail')
    context = {
        'loopdata': [1, 2, 3, 4, 5],
        'stocks': stocks,
        'curr': curr,
    }
    return render(request, 'creditReceipt.html', context)



def customers(request):
    curry = Currency.objects.filter(code='SSP')
    cart = Cart.objects.filter(status='1', receiptNumber=get_cookie(request))
    # cookie = get_cookie(request)
    cookie = get_code()
    for currr in curry:
        curr = currr.factor
    if request.method == 'POST':
        if 'Receipttotal' in request.POST:
            Receipttot = request.POST['Receipttotal'] 
            convertedValue = request.POST['convertedValue'] 
            # cr = CustomerReceipt()

            try:
                receiptNumber = request.POST.get('chequeNo')
                customerName= request.POST.get('customerName')
                modeOfPayment= request.POST.get('modeOfPayment')
                item_purchased= request.POST.get('ice-cream-choice')
                item = get_object_or_404(Stock, inventoryPart=item_purchased)
                purchasedFrom= request.POST.get('purchasedFrom')
                quantity= request.POST.get('quantity')
                price= request.POST.get('price')
                totalAmountPaid= request.POST.get('totalAmountPaid')
                date= request.POST.get('date')
                
                CustomerReceipt.objects.create(
                    receiptNumber=receiptNumber,
                    customerName=customerName,
                    modeOfPayment=modeOfPayment,
                    item_purchased=item,
                    purchasedFrom=purchasedFrom,
                    quantity=quantity,
                    price=price,
                    totalAmountPaid=totalAmountPaid,
                    date=date,
                    ) 
                

                acc = Account.objects.get(name='SJ & Firdous')
                
                if convertedValue == '1':
                    finValue = float(Receipttot) * float(curr)
                    
                    acc.cashFromReceipts += float(finValue)
                    
                    # acc.save()
                else:
                    acc.cashFromReceipts += float(Receipttot)
                    
                    # acc.save()
                return HttpResponse('success')
            except Account.DoesNotExist:
                return HttpResponse('Fail')
               
        return HttpResponse('Fail')


    if request.user.is_staff:
        customers = Customer.objects.all()
        stocks = Stock.objects.all()
        customercount = Customer.objects.all().count()
        stockscount = Stock.objects.all().count()
        vendorcount = Vendor.objects.all().count()
        context = {'customers':customers,
                    'customercount':customercount,
                    'stockscount':stockscount,
                    'vendorcount':vendorcount,
                    'cash':cash,
                    'curr':curr,
                    'cart':cart,
                    'cookie': cookie
              }
    # customers = Customer.objects.filter(addedby=request.user)
    customers = Customer.objects.all()
    stocks = Stock.objects.all()
    
    customercount = Customer.objects.all().count()
    
    context = {'customers':customers,
                'stocks':stocks,
                'customercount':customercount,
                'curr':curr,
                'cart':cart,
                'cookie': cookie
              }
    
    for stock in stocks:
        #print(inventory)
        if request.user.is_staff and stock.piecesQuantity < 1:
            #print(inventory)
            messages.warning(request, stock.inventoryPart+' are running low in stock Please add more!!')
            return render(request, 'index.html', context)
    
    for customer in customers:
        # if (customer.due_date )
        if customer.is_past_due and customer.due_date != None:
            messages.warning(request, customer.customerName+'\'s due date of '+customer.due_date.strftime("%Y-%m-%d")+ ' is past, please follow up and update!!')
            return render(request, 'customers.html', context)
        
    return render(request,'customers.html',context)


@login_required
def inventory(request):
    stocks = Stock.objects.all()
    for stockProfit in stocks:
        percstockProfit = (stockProfit.sellingPrice - stockProfit.costPrice) 
        if stockProfit.piecesQuantity < 2:
            messages.warning(request, stockProfit.inventoryPart+' are RUNNING LOW, please Restock')
                

    context ={'stocks':stocks,
              'percstockProfit':percstockProfit
              }
    return render(request, 'inventory.html', context)

@login_required
def cart(request):
    curry = Currency.objects.filter(code='USD')
    currency = request.session['currency']
    for currr in curry:
        curr = currr.factor
    cst = Cart.objects.filter(status=0, receiptNumber=get_cookie(request)).annotate(totals=Sum('amount'))
    tot = 0
    for k in cst:
        tot += float(k.amount)
    total = tot
    ct_array =  Cart.objects.filter(status=0, receiptNumber=get_cookie(request))
    if request.method == 'POST':
        search = request.POST['search']
        stocks = Stock.objects.all()
        qty_msg = ''
        try:
            stk = Stock.objects.filter(inventoryPart=search)
            if stk:
                for x in stk:
                    check = Cart.objects.filter(item_purchased=search, status=0, receiptNumber=get_cookie(request))
                    if check:
                       for a in check:
                            qty = int(a.quantity)+1 
                            amount = float(a.price) * qty
                            if qty <= int(x.piecesQuantity):
                                Cart.objects.filter(item_purchased=search, status=0, receiptNumber=get_cookie(request)).update(quantity=qty, amount=amount)
                            else:
                                qty_msg = 'Quantity not available'
                    else:
                        if currency == 'SSP':
                            amt = x.sellingPrice
                        else:
                            amt = x.usdPrice
                        Cart.objects.create(cartNo=get_code(), receiptNumber=get_cookie(request), item_purchased=x.inventoryPart, quantity=1, 
                    price=amt, amount=amt, status=0)
                
                cty = Cart.objects.filter(status=0, receiptNumber=get_cookie(request)).annotate(totals=Sum('amount'))
                tt = 0
                for m in cty:
                    tt += float(m.amount)
                ctotal = tt
                cx_array =  Cart.objects.filter(status=0, receiptNumber=get_cookie(request))
                ctx = {'error': 'Item found','cart': cx_array, 'qty_msg': qty_msg, 'amount': ctotal, 
                'usd_total': float(int(ctotal) / curr), 'stocks':stocks, 'currency': currency}
            else:
                ctx = {'error': 'Item not found','qty_msg': '', 'cart': ct_array, 'amount': total, 'usd_total': float(int(total) / curr),
                'stocks':stocks, 'currency': currency}
            return render(request, 'cart.html', ctx)
        except Account.DoesNotExist:
            return HttpResponse('Fail')
    else:
        if request.user.is_staff:
            cash = CashInvoice.objects.all()
            stocks = Stock.objects.all()
            customercount = CashInvoice.objects.all().count()
            stockscount = Stock.objects.all().count()
            vendorcount = Vendor.objects.all().count()
            context = {'cash': cash,
                    'customercount': customercount,
                    'stockscount': stockscount,
                    'vendorcount': vendorcount,
                    'cash': cash,
                    'curr':curr,
                    }
        cash = CashInvoice.objects.all()
        customercount = CashInvoice.objects.all().count()
        context = { 'cash': cash, 'stocks': stocks, 'customercount': customercount, 'curr':curr, 
        'amount': total, 'cart': ct_array, 'usd_total': float(int(total) / curr), 'currency': currency}
    return render(request, 'cart.html',context)


def editCart(request):
    cart_id = int(request.GET.get('pid', ''))
    quantity = int(request.GET.get('text', ''))
    chk = Cart.objects.filter(cartNo=cart_id)
    for a in chk:
        search = a.item_purchased
    try:
        stk = Stock.objects.filter(inventoryPart=search)
        if stk:
            for x in stk:
                check = Cart.objects.filter(cartNo=cart_id)
                if check:
                    for a in check:
                        price = float(a.price)
            amount = float(price) * quantity
            if quantity <= int(x.piecesQuantity):
                Cart.objects.filter(cartNo=cart_id).update(quantity=quantity, amount=amount)
            else:
                return HttpResponse('failed')
            return redirect("cart")
    except Account.DoesNotExist:
        return HttpResponse('Fail')
    
@login_required
def cash(request):
    curry = Currency.objects.filter(code='SSP')
    for currr in curry:
        curr = currr.factor
    if request.method == 'POST':
        if 'Receipttotal' in request.POST:
            Receipttot = request.POST['Receipttotal']
            convertedValue = request.POST['convertedValue'] 
            # accounts = Account.objects.filter(name='SJ & Firdous').order_by('-id')[0]

            try:
                acc = Account.objects.get(name='SJ & Firdous')
                
                print(convertedValue)
                if convertedValue == '1':
                    finValue = float(Receipttot) * float(curr)
                    
                    acc.cashFromReceipts += float(finValue)
                    
                    print(acc.cashFromReceipts)
                    acc.save()
                else:
                    acc.cashFromReceipts += float(Receipttot)
                    
                    print(acc.cashFromReceipts)
                    acc.save()
                print(acc.cashFromReceipts)
                return HttpResponse('success')
            except Account.DoesNotExist:
                return HttpResponse('Fail')

        return HttpResponse('Fail')

    if request.user.is_staff:
        cash = CashInvoice.objects.all()
        stocks = Stock.objects.all()
        customercount = CashInvoice.objects.all().count()
        stockscount = Stock.objects.all().count()
        vendorcount = Vendor.objects.all().count()
        context = {'cash': cash,
                   'customercount': customercount,
                   'stockscount': stockscount,
                   'vendorcount': vendorcount,
                   'cash': cash,
                   'curr':curr,
                   }
    # customers = Customer.objects.filter(addedby=request.user)
    cash = CashInvoice.objects.all()
    # print(customers)

    customercount = CashInvoice.objects.all().count()

    context = {'cash': cash,
               'stocks': stocks,
               'customercount': customercount,
               'curr':curr,
               }

    for stock in stocks:
        # print(inventory)
        if request.user.is_staff and stock.piecesQuantity < 1:
            # print(inventory)
            messages.warning(request, stock.inventoryPart + ' are running low in stock Please add more!!')
            return render(request, 'index.html', context)

    # for customer in customers:
    #     # if (customer.due_date )
    #     if customer.is_past_due and customer.due_date != None:
    #         messages.warning(request, customer.customerName + '\'s due date of ' + customer.due_date.strftime(
    #             "%Y-%m-%d") + ' is past, please follow up and update!!')
    #         return render(request, 'customers.html', context)

    return render(request, 'cash.html',context)

@login_required
def purchase(request):
    purchase = PurchaseOrder.objects.all()
    
    context ={'purchase':purchase
              }
    return render(request, 'purchase.html',context)

@login_required
def check(request):
    checks = Cheques.objects.all()
    
    context ={'checks':checks
              }
    return render(request, 'check.html',context)

@login_required
def PurchaseReport(request):

    return render(request, 'purchase-report.html')
@login_required
def ExpenseReport(request):

    return render(request, 'expense-report.html')
def StockReport(request):

    return render(request, 'stock-report.html')
@login_required
def SalesReport(request):
    return render(request, 'sales-report.html')
def ProfitLossReport(request):
    return render(request, 'profit-and-loss.html')
@login_required
def payable(request):
    payables = Payable.objects.all()
    
    context = {'payables': payables
               }
    return render(request, 'payable.html', context)

@login_required
def transfer(request):
    transfers = Transfer.objects.all()
    
    context = {'transfers': transfers
               }
    return render(request, 'transfer.html',context)

@login_required
# def Receipts(request):
#     # transfers = Transfer.objects.all()
#     #
#     # context = {'transfers': transfers
#     #            }
#     return render(request, 'receipts.html')
def Receivepayment_detail(request,pk):
    inventorys = Stock.objects.all()
    customer = get_object_or_404(CashInvoice, pk=pk)

    # print(customer.name)
    if request.method == "POST":

        if "editcustomer" in request.POST:

            customer.customerName = request.POST["name"]
            customer.receiptNumber = request.POST["number"]

            inventoryid = request.POST["inventory_purchased"]
            customer.inventory_purchased = get_object_or_404(Stock, id=inventoryid)

            customer.quantity = request.POST["quantity"]

            inventory = Stock.objects.get(id=inventoryid)
            if int(customer.quantity) < inventory.quantity:
                inventory.quantity -= int(customer.quantity)
                inventory.save()

                customer.amount = request.POST["amount"]
                customer.balance = inventory.price * int(customer.quantity) - int(customer.amount) * int(
                    customer.quantity)
                customer.addedby = request.user
                customer.save()

                messages.warning(request, 'Customer updated Successfully!!')
                return redirect('index')
            else:
                messages.warning(request, 'Not enough inventory in stock, please contact Administrator')
                return redirect('index')

    context = {'customer': customer, 'inventorys': inventorys}

    return render(request,'invoicepayment_detail.html')

def Writecheques_detail(request,pk):
    # cheqs = Cheques.objects.all()
    cheqs = get_object_or_404(Cheques, pk=pk)
    if request.method == "POST":

        if "editcheque" in request.POST:

            cheqs.name = request.POST["name"]
            cheqs.number = request.POST["number"]

            inventoryid = request.POST["inventory_purchased"]
            cheqs.inventory_purchased = get_object_or_404(Stock, id=inventoryid)

            cheqs.quantity = request.POST["quantity"]

            inventory = Stock.objects.get(id=inventoryid)
            if int(cheqs.quantity) < inventory.quantity:
                inventory.quantity -= int(cheqs.quantity)
                inventory.save()

                cheqs.amount = request.POST["amount"]
                cheqs.balance = inventory.price * int(cheqs.quantity) - int(cheqs.amount) * int(
                    cheqs.quantity)
                cheqs.addedby = request.user
                cheqs.save()

                messages.warning(request, 'Customer updated Successfully!!')
                return redirect('index')
            else:
                messages.warning(request, 'Not enough inventory in stock, please contact Administrator')
                return redirect('index')

    context = {'cheqs': cheqs}

    return render(request,'cheques_detail.html',context)

def Transferdetail(request,pk):
    # cheqs = Cheques.objects.all()
    transfer = get_object_or_404(Transfer, pk=pk)
    if request.method == "POST":

        if "editcheque" in request.POST:

            transfer.name = request.POST["name"]
            transfer.number = request.POST["number"]

            inventoryid = request.POST["inventory_purchased"]
            transfer.inventory_purchased = get_object_or_404(Stock, id=inventoryid)

            transfer.quantity = request.POST["quantity"]

            inventory = Stock.objects.get(id=inventoryid)
            if int(transfer.quantity) < inventory.quantity:
                inventory.quantity -= int(transfer.quantity)
                inventory.save()

                transfer.amount = request.POST["amount"]
                transfer.balance = inventory.price * int(transfer.quantity) - int(transfer.amount) * int(
                    transfer.quantity)
                transfer.addedby = request.user
                transfer.save()

                messages.warning(request, 'Customer updated Successfully!!')
                return redirect('index')
            else:
                messages.warning(request, 'Not enough inventory in stock, please contact Administrator')
                return redirect('index')

    context = {'transfer': transfer}

    return render(request,'transfer_detail.html',context)
def Payabledetail(request,pk):
    # cheqs = Cheques.objects.all()
    pay = get_object_or_404(Payable, pk=pk)
    if request.method == "POST":

        if "editcheque" in request.POST:

            pay.vendorSupplied = request.POST["name"]
            pay.item_supplied = request.POST["number"]

            inventoryid = request.POST["inventory_purchased"]
            #transfer.inventory_purchased = get_object_or_404(Stock, id=inventoryid)

            transfer.quantity = request.POST["quantity"]

            inventory = Stock.objects.get(id=inventoryid)
            if int(transfer.quantity) < inventory.quantity:
                inventory.quantity -= int(transfer.quantity)
                inventory.save()

                transfer.amount = request.POST["amount"]
                transfer.balance = inventory.price * int(transfer.quantity) - int(transfer.amount) * int(
                    transfer.quantity)
                transfer.addedby = request.user
                transfer.save()

                messages.warning(request, 'Customer updated Successfully!!')
                return redirect('index')
            else:
                messages.warning(request, 'Not enough inventory in stock, please contact Administrator')
                return redirect('index')

    context = {'pay': pay}

    return render(request,'payable_detail.html',context)
#
#
# def paymentReceipt(request):
#     # transfers = Transfer.objects.all()
#     #
#     # context = {'transfers': transfers
#     #            }
#     return render(request, 'paymentreceipt.html')
@login_required
def statistics(request):
    # checks = Cheques.objects.all()
    #
    # context = {'checks': checks
    #            }
    return render(request, 'statistics.html')
def Reportsview(request):
    return render(request,'reports.html')

# @login_required
def Createcustomer(request):
    # customer = Customer()
    # inventorys = Inventory.objects.all()
    # if request.method == "POST":
    #
    #     if "createcustomer" in request.POST:
    #
    #         customer.name = request.POST["name"]
    #         customer.number = request.POST["number"]
    #
    #         inventoryid = request.POST["inventory_purchased"]
    #         customer.inventory_purchased = get_object_or_404(Inventory, id=inventoryid)
    #
    #         customer.quantity = request.POST["quantity"]
    #
    #         inventory = Inventory.objects.get(id=inventoryid)
    #
    #         if int(customer.quantity) < inventory.quantity:
    #             inventory.quantity -= int(customer.quantity)
    #             inventory.save()
    #             customer.amount = request.POST["amount"]
    #             customer.balance = inventory.price * int(customer.quantity) - int(customer.amount) * int(
    #                 customer.quantity)
    #             customer.addedby = request.user
    #             customer.save()
    #
    #             messages.success(request, 'New Customer added Successfully!!')
    #             return redirect('index')
    #
    #         else:
    #             messages.warning(request, inventory.name + ' are NOT enough in stock, please contact Administrator')
    #             return redirect('index')
    #
    # context = {'inventorys': inventorys
    #            }
    return render(request, 'customer_create.html')

@login_required
def cashSales(request):
    curry = Currency.objects.filter(code='USD')
    for currr in curry:
        curr = currr.factor
    stocks = Stock.objects.all()
    receipts = CustomerReceipt.objects.all()
    context = {'stocks':stocks, 'curr': curr, "receipts": receipts}
    return render(request,'sales.html', context)


@login_required
def viewCredit(request):
    curry = Currency.objects.filter(code='USD')
    for currr in curry:
        curr = currr.factor
    stocks = Stock.objects.all()
    receipts = CreditReceipt.objects.all()
    context = {'stocks':stocks, 'curr': curr, "receipts": receipts}
    return render(request,'credit.html', context)

@login_required
def viewQuotation(request):
    curry = Currency.objects.filter(code='USD')
    for currr in curry:
        curr = currr.factor
    stocks = Stock.objects.all()
    receipts = QuotationReceipt.objects.all()
    context = {'stocks':stocks, 'curr': curr, "receipts": receipts}
    return render(request,'quotation.html', context)

@login_required
def previewReceipt(request, receipt):
    curry = Currency.objects.filter(code='USD')
    for currr in curry:
        curr = currr.factor
    cst = Cart.objects.filter(status=1, receiptNumber=receipt).annotate(totals=Sum('amount'))
    tot = 0
    method = []
    for k in cst:
        tot += float(k.amount)
        method.append(str(k.type))
    if method[0] == 'Cash':
        t = CustomerReceipt.objects.filter(receiptNumber=receipt)
        for m in t:
            total = float(m.totalAmountPaid)
            discount = float(m.discount)
            currency = str(m.currency)
            mode = str(m.modeOfPayment)
            cname = str(m.customerName)
            purchased = str(m.purchasedFrom)
            ptype = str(m.payType)
    elif method[0] == 'Credit':
        t = CreditReceipt.objects.filter(creditNumber=receipt)
        for m in t:
            total = float(m.totalAmountPaid)
            discount = float(m.discount)
            currency = str(m.currency)
            mode = str(m.modeOfPayment)
            cname = str(m.customerName)
            purchased = str(m.purchasedFrom)
            ptype = str(m.payType)
    else:
        t = QuotationReceipt.objects.filter(quotationNumber=receipt)
        for m in t:
            total = float(m.totalAmountPaid)
            discount = float(m.discount)
            currency = str(m.currency)
            mode = str(m.modeOfPayment)
            cname = str(m.customerName)
            purchased = str(m.purchasedFrom)
            ptype = str(m.payType)
    usd_total = float(int(total) / curr)
    usd_disc = float(int(discount) / curr)
    stocks = Stock.objects.all()
    receipts = Cart.objects.filter(receiptNumber=receipt, status=1)
    context = {'stocks': stocks, 'curr': curr, "receipts": receipts, "total": total, 
    "usd_total": usd_total, "method": method[0], "usd_disc": usd_disc,"discount": discount, 
    "currency": currency, "receipt": receipt, "customer": cname, "mode": mode, 'purchased': purchased, 'payMethod':ptype}
    return render(request,'cashReceipt.html', context)

def deleteCart(request, pk):
    cart = get_object_or_404(Cart, pk=pk)
    if cart:
        Cart.objects.filter(cartNo=pk).delete()
    else:
        return HttpResponse('Failed to delete')
    return redirect("cart")

def Customerdetailfunc(request, pk):
    # inventorys = Stock.objects.all()
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":

        if "editcustomer" in request.POST:

            customer.name = request.POST["name"]
            customer.number = request.POST["number"]

            inventoryid = request.POST["inventory_purchased"]
            customer.inventory_purchased = get_object_or_404(Stock, id=inventoryid)

            customer.quantity = request.POST["quantity"]

            inventory = Stock.objects.get(id=inventoryid)
            if int(customer.quantity) < inventory.quantity:
                inventory.quantity -= int(customer.quantity)
                inventory.save()

                customer.amount = request.POST["amount"]
                customer.balance = inventory.price * int(customer.quantity) - int(customer.amount) * int(
                    customer.quantity)
                customer.addedby = request.user
                customer.save()

                messages.warning(request, 'Customer updated Successfully!!')
                return redirect('index')
            else:
                messages.warning(request, 'Not enough inventory in stock, please contact Administrator')
                return redirect('index')

    context = {'customer': customer}

    return render(request, 'customer_detail.html', context)


# @login_required
def Createworkorder(request):
    # workorder = Workorder()
    # jobtypes = JobType.objects.all()
    # customers = Customer.objects.filter(addedby=request.user)
    # technicians = Technician.objects.all()
    # if request.method == "POST":
    #
    #     if "createworkorder" in request.POST:
    #         workorder.ordername = request.POST["ordername"]
    #         # workorder.number = request.POST["number"]
    #         customerid = request.POST["name"]
    #         workorder.customer_name = get_object_or_404(Customer, id=customerid)
    #
    #         jobid = request.POST["jobtype"]
    #         workorder.jobtype = get_object_or_404(JobType, id=jobid)
    #
    #         techid = request.POST["technician"]
    #         workorder.technician = get_object_or_404(Technician, id=techid)
    #
    #         workorder.order_status = request.POST["status"]
    #
    #         workorder.amount_paid = request.POST["amount"]
    #         workorder.balance = request.POST["balance"]
    #         workorder.save()
    #
    #         messages.success(request, 'Workorder added Successfully!!')
    #         return redirect('index')
    #
    # context = {'customers': customers, 'jobtypes': jobtypes, 'technicians': technicians
    #            }
    return render(request, 'workorder_create.html')


# @login_required
def Workorderdetailfunc(request, pk):
    # jobtypes = JobType.objects.all()
    # customers = Customer.objects.filter(addedby=request.user)
    # technicians = Technician.objects.all()
    # workorder = get_object_or_404(Workorder, pk=pk)
    # if request.method == "POST":
    #
    #     if "editworkorder" in request.POST:
    #         workorder.ordername = request.POST["ordername"]
    #         # workorder.number = request.POST["number"]
    #         customerid = request.POST["name"]
    #         workorder.customer_name = get_object_or_404(Customer, id=customerid)
    #
    #         jobid = request.POST["jobtype"]
    #         workorder.jobtype = get_object_or_404(JobType, id=jobid)
    #
    #         techid = request.POST["technician"]
    #         workorder.technician = get_object_or_404(Technician, id=techid)
    #
    #         workorder.order_status = request.POST["status"]
    #
    #         workorder.amount_paid = request.POST["amount"]
    #         workorder.balance = request.POST["balance"]
    #         workorder.save()
    #
    #         messages.success(request, 'Workorder Updated Successfully!!')
    #         return redirect('workorders')
    #
    # context = {'customers': customers, 'jobtypes': jobtypes, 'technicians': technicians, 'workorder': workorder
    #            }
    return render(request, 'workorder_detail.html')


# @login_required
def Createreturnjob(request):
    # returnjob = ReturnJobs()
    # customers = Customer.objects.filter(addedby=request.user)
    # if request.method == "POST":
    #
    #     if "createreturnjob" in request.POST:
    #         returnjob.jobname = request.POST["rjname"]
    #         # workorder.number = request.POST["number"]
    #         customerid = request.POST["name"]
    #         returnjob.customer_name = get_object_or_404(Customer, id=customerid)
    #         returnjob.complaint = request.POST["complaint"]
    #         returnjob.partnumber = request.POST["partnumber"]
    #         returnjob.datedone = request.POST["datedone"]
    #         returnjob.status = request.POST["statusr"]
    #         returnjob.save()
    #
    #         messages.success(request, 'Returnjob added Successfully!!')
    #         return redirect('returnjobs')
    #
    # context = {'customers': customers
    #           }
    return render(request, 'returnjob_create.html')


# @login_required
def Returnjobdetailfunc(request, pk):
    # customers = Customer.objects.filter(addedby=request.user)
    #
    # returnjob = get_object_or_404(ReturnJobs, pk=pk)
    # if request.method == "POST":
    #
    #     if "updatereturnjob" in request.POST:
    #         returnjob.jobname = request.POST["rjname"]
    #         # workorder.number = request.POST["number"]
    #         customerid = request.POST["name"]
    #         returnjob.customer_name = get_object_or_404(Customer, id=customerid)
    #
    #         returnjob.complaint = request.POST["complaint"]
    #         returnjob.partnumber = request.POST["partnumber"]
    #         returnjob.datedone = request.POST["datedone"]
    #         returnjob.status = request.POST["statusr"]
    #
    #         returnjob.save()
    #
    #         messages.success(request, 'Return Job Updated Successfully!!')
    #         return redirect('returnjobs')
    #
    # context = {'customers': customers, 'returnjob': returnjob
    #            }
    return render(request, 'returnjob_detail.html')

# @login_required
def workorder(request):
    # workorders = Workorder.objects.all()
    # context ={'workorders':workorders
    #          }
    return render(request, 'workorder.html', context)


# @login_required
def ReturnJobo(request):
    # returnjobs = ReturnJobs.objects.all()
    # context ={'returnjobs':returnjobs
    #           }
    return render(request, 'returnjobs.html')


# def ReportPdf(request):
#     # creating a byteStream Buffer
#     buf = io.BytesIO()
#     # create a canvas 
#     c = canvas.Canvas(buf,pagesize=letter, bottomup=0)   
#     # create a text object
#     textob = c.beginText()
#     textob.setTextOrigin(inch, inch)
#     textob.setFont("Helvetica", 14)


    # Adding some lines of text
    # lines = [
    #     "This is line 1",
    #     "This is line 2",
    #     "This is line 3"
    # ]

    # # Designate the model
    # customer = Customer.objects.all()

    # # Create blank list
    # lines = []

    # for customer in customer:
    #     lines.append(customer.customerName)
    #     lines.append(customer.contact)
    #     lines.append(customer.item_purchased)
    #     lines.append(customer.quantity)
    #     lines.append("-----------------")

    # # loop 
    # for line in lines:
    #     textob.textLine(line)

    # # Finish up
    # c.drawText(textob)
    # c.showPage()
    # c.save()
    # buf.seek(0)

    # # return 
    # return FileResponse(buf, as_attachment=True, filename='report.pdf')

@login_required
def selectcurrency(request):
    lasturl = request.META.get('HTTP_REFERER')
    if request.method == 'POST':  # check post
        request.session['currency'] = request.POST['currency']
    return HttpResponseRedirect(lasturl)

# @login_required(login_url='/login') # Check login
# def savelangcur(request):
#     lasturl = request.META.get('HTTP_REFERER')
#     curren_user = request.user
#     language=Language.objects.get(code=request.LANGUAGE_CODE[0:2])
#     #Save to User profile database
#     data = UserProfile.objects.get(user_id=curren_user.id )
#     data.language_id = language.id
#     data.currency_id = request.session['currency']
#     data.save()  # save data
#     return HttpResponseRedirect(lasturl)