from django.contrib import admin
from .models import *

# Register your models here.

class StockAdmin(admin.ModelAdmin):
    list_display = ['inventoryPart','picture_tag', 'costPrice','piecesQuantity','vendorSupplied']
    readonly_fields = ['percentageProfit']
    search_fields = ['inventoryPart']

class CustomerAdmin(admin.ModelAdmin):
    search_fields = ['customerName']
    list_display = ['customerName','item_purchased','quantity', 'order_status','date', 'due_date']
    readonly_fields = ['balance','order_status']

class AccountAdmin(admin.ModelAdmin):
    list_display = ['name','cashAccount','bankAccount', 'debtorBalance', 'accountBalance','expensesTotal','grandTotal','updated_at']
    readonly_fields = ['name','cashAccount','bankAccount', 'debtorBalance', 'accountBalance','expensesTotal','grandTotal','updated_at']
class PurchaseOrderAdmin(admin.ModelAdmin):
    readonly_fields = ['balance']

class CashInvoiceAdmin(admin.ModelAdmin):
    readonly_fields = ['balance']

class ChequesAdmin(admin.ModelAdmin):
    readonly_fields = ['balance']

class TransferAdmin(admin.ModelAdmin):
    readonly_fields = ['Balance','status']

class CustomerReceiptAdmin(admin.ModelAdmin):
    list_display = ['receiptNumber','customerName']
    search_fields = ['receiptNumber', 'customerName']

class QuotationReceiptAdmin(admin.ModelAdmin):
    list_display = ['quotationNumber','customerName']
    search_fields = ['quotationNumber', 'customerName']


class CreditReceiptAdmin(admin.ModelAdmin):
    list_display = ['creditNumber','customerName']
    search_fields = ['creditNumber', 'customerName']

admin.site.register(Vendor),
admin.site.register(Stock,StockAdmin),
admin.site.register(Customer, CustomerAdmin),
# admin.site.register(ExchangeRate),
admin.site.register(CashInvoice, CashInvoiceAdmin),
admin.site.register(PurchaseOrder, PurchaseOrderAdmin),
admin.site.register(Cheques,ChequesAdmin),
admin.site.register(Payable),
admin.site.register(Cart),
admin.site.register(CustomerReceipt,CustomerReceiptAdmin),
admin.site.register(QuotationReceipt,QuotationReceiptAdmin),
admin.site.register(CreditReceipt,CreditReceiptAdmin)
admin.site.register(Account,AccountAdmin),
admin.site.register(Transfer,TransferAdmin),



