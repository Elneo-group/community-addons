import pytz
from _datetime import datetime
import logging
import requests
import xml.etree.ElementTree as etree
from odoo import models, fields, api, _
from odoo.addons.tnt_shipping_integration.models.tnt_response import Response
from odoo.exceptions import Warning, ValidationError, UserError
from requests.auth import HTTPBasicAuth
import urllib.parse

_logger = logging.getLogger("TNT")


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("tnt", "TNT")])
    package_id = fields.Many2one('product.packaging', string="package", help="please select package type")
    content_type = fields.Selection([('D', 'D-Document'),
                                     ('N', 'N-Non-document')], help="TNT Content type")
    payment_indication = fields.Selection([('S', 'S-Sender'),
                                           ('R', 'R-Receiver')])
    tnt_service_code = fields.Selection([('48N', '48N - Economy Express(Internacional)(NON DOC)'),
                                         ('412', '412 - 12:00 Economy Express(Internacional)(NON DOC)'),
                                         ('15D', '15D - Express(Internacional/Domestic)(DOC)'),
                                         ('15N', '15N - Express(Internacional/Domestic)(NON DOC)'),
                                         ('09D', '09D - 9:00 Express(Internacional)(DOC)'),
                                         ('09N', '09N - 9:00 Express(Internacional)(NON DOC)'),
                                         ('10D', '10D - 10:00 Express(Internacional/Domestic)(DOC)'),
                                         ('10N', '10N - 10:00 Express(Internacional/Domestic)(NON DOC)'),
                                         ('12D', '10N - 12:00 Express(Internacional/Domestic)(DOC)'),
                                         ('12N', '12N - 12:00 Express(Internacional/Domestic)(NON DOC)'),
                                         ('15', '15 - Express Plus(Domestic)(NON DOC)')])
    tnt_option = fields.Selection([('PR', 'PR-Priority'),
                                   ('BB', 'BB-Biological SubStance Cat.B'),
                                   ('DI', 'DI-Dry Ice'),
                                   ('LB', 'LB-Section || SP188Lithium Bat')],string="TNT Option")

    def tnt_rate_shipment(self, order):
        "This Method Is Used For Get Rate"
        weight = sum(
            [(line.product_id.weight * line.product_uom_qty) for line in order.order_line if not line.is_delivery])
        uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        total_weight = round(weight * 2.20462, 3) if uom_id.name in ["lb", "lbs"] else round(weight, 3)
        shipper_address = order.warehouse_id and order.warehouse_id.partner_id
        recipient_address = order.partner_shipping_id
        price_request = etree.Element("priceRequest")
        etree.SubElement(price_request, 'appId').text = str(self.company_id and self.company_id.tnt_app_id)
        etree.SubElement(price_request, 'appVersion').text = "3.0"
        price_check = etree.SubElement(price_request, "priceCheck")
        etree.SubElement(price_check, 'rateId').text = "rate1"
        sender_node = etree.SubElement(price_check, "sender")
        etree.SubElement(sender_node, 'country').text = str(
            shipper_address.country_id and shipper_address.country_id.code or "")
        etree.SubElement(sender_node, 'town').text = shipper_address and shipper_address.city or ""
        etree.SubElement(sender_node, 'postcode').text = str(shipper_address and shipper_address.zip or "")
        receiver_node = etree.SubElement(price_check, "delivery")
        etree.SubElement(receiver_node, 'country').text = str(
            recipient_address.country_id and recipient_address.country_id.code or "")
        etree.SubElement(receiver_node, 'town').text = str(recipient_address and recipient_address.city or "")
        etree.SubElement(receiver_node, 'postcode').text = str(recipient_address and recipient_address.zip or "")
        etree.SubElement(price_check, 'collectionDateTime').text = datetime.strftime(datetime.now(pytz.utc),
                                                                                     "%Y-%m-%dT%H:%M:%S")  #"2021-03-04T11:38:00"
        product = etree.SubElement(price_check, "product")
        etree.SubElement(product, 'id').text = str(self.tnt_service_code or "")
        etree.SubElement(product, 'type').text = str(self.content_type or "")
        etree.SubElement(price_check, 'currency').text = str(order.currency_id.name or "")
        consignment_details = etree.SubElement(price_check, "consignmentDetails")
        etree.SubElement(consignment_details, 'totalWeight').text = str(total_weight)
        etree.SubElement(consignment_details, 'totalVolume').text = str(
            (self.package_id and self.package_id.length or 1) * (self.package_id and self.package_id.height or 1) * (
                        self.package_id and self.package_id.width or 1))
        etree.SubElement(consignment_details, 'totalNumberOfPieces').text = "1"
        piece_line = etree.SubElement(price_check, "pieceLine")
        etree.SubElement(piece_line, 'numberOfPieces').text = "1"
        piece_measurements = etree.SubElement(piece_line, "pieceMeasurements")
        etree.SubElement(piece_measurements, 'length').text = str(self.package_id and self.package_id.length or 0.0)
        etree.SubElement(piece_measurements, 'width').text = str(self.package_id and self.package_id.height or 0.0)
        etree.SubElement(piece_measurements, 'height').text = str(self.package_id and self.package_id.width or 0.0)
        etree.SubElement(piece_measurements, 'weight').text = str(weight)
        etree.SubElement(piece_line, 'pallet').text = ""
        try:
            username = self.company_id.tnt_company
            password = self.company_id.tnt_password
            headers = {'SOAPAction': '', 'Content-Type': ''}
            url = "{}/pricing/getprice".format(self.company_id and self.company_id.tnt_api_url)
            response_data = requests.request(method="POST", url=url, headers=headers,
                                             auth=HTTPBasicAuth(username=username, password=password),
                                             data=etree.tostring(price_request))
            if response_data.status_code in [200, 201]:
                api = Response(response_data.content)
                response_data = api.dict()
                _logger.info(response_data)
                if response_data.get('document') and response_data.get('document').get('priceResponse') == None:
                    raise ValidationError("TNT Rate Response Issue : %s" % (response_data))
                rated_services = response_data.get('document') and response_data.get('document').get(
                    'priceResponse') and response_data.get('document').get('priceResponse').get('ratedServices') and \
                                 response_data.get('document').get('priceResponse').get('ratedServices').get(
                                     'ratedService')
                shipping_charge = 0.0
                if isinstance(rated_services, dict):
                    rated_services = [rated_services]
                for rated_service in rated_services:
                    if not shipping_charge:
                        shipping_charge = float(rated_service.get('totalPrice'))
                    shipping_charge = min(float(rated_service.get('totalPrice')), shipping_charge)
                return {'success': True, 'price': shipping_charge, 'error_message': False, 'warning_message': False}
        except Exception as e:
            raise ValidationError(e)

    @api.model
    def tnt_send_shipping(self, pickings):
        """This Method Is Used For Send The Data To Shipper"""

        response = []
        for picking in pickings:
            total_bulk_weight = picking.weight_bulk  # picking.weight_bulk
            picking_partner_id = picking.partner_id
            picking_company_id = picking.picking_type_id.warehouse_id.partner_id

            # Header Tag
            tag = '''<?xml version="1.0" encoding="utf-8" standalone="no"?><?xml-stylesheet href="https://express.tnt.com/expresswebserviceswebsite/stylesheets/HTMLConsignmentNoteRenderer.xsl" type="text/xsl"?>'''
            shipment_request = etree.Element("ESHIPPER")

            # Sub Tag
            login = etree.SubElement(shipment_request, "LOGIN")
            etree.SubElement(login, 'COMPANY').text = str(self.company_id and self.company_id.tnt_company or "")
            etree.SubElement(login, 'PASSWORD').text = str(self.company_id and self.company_id.tnt_password or "")
            etree.SubElement(login, 'APPID').text = str(self.company_id and self.company_id.tnt_app_id or "")
            etree.SubElement(login, 'APPVERSION').text = "3.0"

            # Sub Tag consignmentbatch
            consignmentbatch = etree.SubElement(shipment_request, "CONSIGNMENTBATCH")
            sender = etree.SubElement(consignmentbatch, "SENDER")
            etree.SubElement(sender, 'COMPANYNAME').text = str(picking_company_id and picking_company_id.name or "")
            etree.SubElement(sender, 'STREETADDRESS1').text = str(picking_company_id and picking_company_id.street or "")
            etree.SubElement(sender, 'CITY').text = str(picking_company_id and picking_company_id.city or "")
            etree.SubElement(sender, 'POSTCODE').text = str(picking_company_id and picking_company_id.zip or "")
            etree.SubElement(sender, 'COUNTRY').text = str(picking_company_id.country_id and picking_company_id.country_id.code or "")
            etree.SubElement(sender, 'ACCOUNT').text = str(self.company_id and self.company_id.tnt_account_number or "")
            etree.SubElement(sender, 'CONTACTNAME').text = str(picking_company_id and picking_company_id.name or "")
            etree.SubElement(sender, 'CONTACTDIALCODE').text = str(picking_company_id and picking_company_id.phone or "")
            etree.SubElement(sender, 'CONTACTTELEPHONE').text = str(picking_company_id and picking_company_id.phone or "")
            etree.SubElement(sender, 'CONTACTEMAIL').text = str(picking_company_id and picking_company_id.email or "")

            # sub tag collection
            collection = etree.SubElement(sender, "COLLECTION")
            collection_address = etree.SubElement(collection, "COLLECTIONADDRESS")
            etree.SubElement(collection_address, 'COMPANYNAME').text = str(picking_company_id and picking_company_id.name or "")
            etree.SubElement(collection_address, 'STREETADDRESS1').text = str(picking_company_id and picking_company_id.street or "")
            etree.SubElement(collection_address, 'CITY').text = str(picking_company_id and picking_company_id.city or "")
            etree.SubElement(collection_address, 'POSTCODE').text = str(picking_company_id and picking_company_id.zip or "")
            etree.SubElement(collection_address, 'COUNTRY').text = str(picking_company_id.country_id and picking_company_id.country_id.code or "")
            etree.SubElement(collection_address, 'CONTACTNAME').text = str(picking_company_id and picking_company_id.name or "")
            etree.SubElement(collection_address, 'CONTACTDIALCODE').text = str(picking_company_id and picking_company_id.phone or "")
            etree.SubElement(collection_address, 'CONTACTTELEPHONE').text = str(picking_company_id and picking_company_id.phone or "")
            etree.SubElement(collection_address, 'CONTACTEMAIL').text = str(picking_company_id and picking_company_id.email or "")

            # sub Tag shipment date
            etree.SubElement(collection, 'SHIPDATE').text = str(picking.scheduled_date.strftime("%d/%m/%Y"))

            # sub tag collection time
            prefcollecttime = etree.SubElement(collection, "PREFCOLLECTTIME")
            etree.SubElement(prefcollecttime, 'FROM').text = "09:00"
            etree.SubElement(prefcollecttime, 'TO').text = "10:00"
            altcollecttime = etree.SubElement(collection, "ALTCOLLECTTIME")
            etree.SubElement(altcollecttime, 'FROM').text = "11:00"
            etree.SubElement(altcollecttime, 'TO').text = "12:00"
            etree.SubElement(collection, 'COLLINSTRUCTIONS').text = "12:00"

            consignment = etree.SubElement(consignmentbatch, "CONSIGNMENT")
            etree.SubElement(consignment, 'CONREF').text = str(picking.origin)
            details_node = etree.SubElement(consignment, "DETAILS")
            receiver_node = etree.SubElement(details_node, "RECEIVER")
            etree.SubElement(receiver_node, 'COMPANYNAME').text = str(picking_partner_id and picking_partner_id.name or "")
            etree.SubElement(receiver_node, 'STREETADDRESS1').text = str(picking_partner_id and picking_partner_id.street or "")
            etree.SubElement(receiver_node, 'CITY').text = str(picking_partner_id and picking_partner_id.city or "")
            etree.SubElement(receiver_node, 'POSTCODE').text = str(picking_partner_id and picking_partner_id.zip or "")
            etree.SubElement(receiver_node, 'COUNTRY').text = str(picking_partner_id.country_id and picking_partner_id.country_id.code or "")
            etree.SubElement(receiver_node, 'CONTACTNAME').text = str(picking_partner_id and picking_partner_id.name or "")
            etree.SubElement(receiver_node, 'CONTACTDIALCODE').text = str(picking_partner_id and picking_partner_id.phone or "")
            etree.SubElement(receiver_node, 'CONTACTTELEPHONE').text = str(picking_partner_id and picking_partner_id.phone or "")
            etree.SubElement(receiver_node, 'CONTACTEMAIL').text = str(picking_partner_id and picking_partner_id.email or "")

            delivery_node = etree.SubElement(details_node, "DELIVERY")
            etree.SubElement(delivery_node, 'COMPANYNAME').text = str(picking_partner_id and picking_partner_id.name or "")
            etree.SubElement(delivery_node, 'STREETADDRESS1').text = str(picking_partner_id and picking_partner_id.street or "")
            etree.SubElement(delivery_node, 'CITY').text = str(picking_partner_id and picking_partner_id.city or "")
            etree.SubElement(delivery_node, 'POSTCODE').text = str(picking_partner_id and picking_partner_id.zip or "")
            etree.SubElement(delivery_node, 'COUNTRY').text = str(picking_partner_id.country_id and picking_partner_id.country_id.code or "")
            etree.SubElement(delivery_node, 'CONTACTNAME').text = str(picking_partner_id and picking_partner_id.name or "")
            etree.SubElement(delivery_node, 'CONTACTDIALCODE').text = str(picking_partner_id and picking_partner_id.phone or "")
            etree.SubElement(delivery_node, 'CONTACTTELEPHONE').text = str(picking_partner_id and picking_partner_id.phone or "")
            etree.SubElement(delivery_node, 'CONTACTEMAIL').text = str(picking_partner_id and picking_partner_id.email or "")

            etree.SubElement(details_node, 'CUSTOMERREF').text = ""
            etree.SubElement(details_node, 'CONTYPE').text = str(self.content_type or "")
            etree.SubElement(details_node, 'PAYMENTIND').text = str(self.payment_indication or "")
            etree.SubElement(details_node, 'ITEMS').text = str(len(picking.package_ids) if picking.package_ids else 1)


            etree.SubElement(details_node, 'TOTALWEIGHT').text = str(picking.shipping_weight)

            etree.SubElement(details_node, 'TOTALVOLUME').text =  str((self.package_id and self.package_id.length or 1) *
                                                                     (self.package_id and self.package_id.height or 1) *
                                                                     (self.package_id and self.package_id.width or 1))
            etree.SubElement(details_node, 'SERVICE').text = str(self.tnt_service_code or "")
            etree.SubElement(details_node, 'OPTION').text = str(self.tnt_option or "")
            etree.SubElement(details_node, 'DESCRIPTION').text = "%s"%(picking.origin)
            etree.SubElement(details_node, 'DELIVERYINST').text = ""
            number_of_packages = 0
            for package_id in picking.package_ids:
                number_of_packages += 1
                package_node = etree.SubElement(details_node, "PACKAGE")
                etree.SubElement(package_node, 'ITEMS').text = str(number_of_packages)
                etree.SubElement(package_node, 'DESCRIPTION').text = "%s"%(package_id.name)
                etree.SubElement(package_node, 'LENGTH').text = str(package_id.packaging_id and package_id.packaging_id.length or 0.0)
                etree.SubElement(package_node, 'HEIGHT').text = str(package_id.packaging_id and package_id.packaging_id.height or 0.0)
                etree.SubElement(package_node, 'WIDTH').text = str(package_id.packaging_id and package_id.packaging_id.width or 0.0)
                etree.SubElement(package_node, 'WEIGHT').text = str(package_id.shipping_weight)
            if total_bulk_weight > 0:
                number_of_packages += 1
                package_node = etree.SubElement(details_node, "PACKAGE")
                etree.SubElement(package_node, 'ITEMS').text = str(number_of_packages)
                etree.SubElement(package_node, 'DESCRIPTION').text = "Bulk Package"
                etree.SubElement(package_node, 'LENGTH').text = "{}".format(self.package_id and self.package_id.length or 0)
                etree.SubElement(package_node, 'HEIGHT').text = "{}".format(self.package_id and self.package_id.height or 0)
                etree.SubElement(package_node, 'WIDTH').text = "{}".format(self.package_id and self.package_id.width or 0)
                etree.SubElement(package_node, 'WEIGHT').text = "{}".format(str(total_bulk_weight))
            activity_node = etree.SubElement(shipment_request, "ACTIVITY")
            create_node = etree.SubElement(activity_node, "CREATE")
            etree.SubElement(create_node, 'CONREF').text = str(picking.origin or "")

            book_node = etree.SubElement(activity_node, "BOOK")
            etree.SubElement(book_node, 'CONREF').text = str(picking.origin or "")

            ship_node = etree.SubElement(activity_node, "SHIP")
            etree.SubElement(ship_node, 'CONREF').text = str(picking.origin or "")

            print_node = etree.SubElement(activity_node, "PRINT")
            connote_node = etree.SubElement(print_node, "CONNOTE")
            etree.SubElement(connote_node, 'CONREF').text = str(picking.origin or "")

            label_node = etree.SubElement(print_node, "LABEL")
            etree.SubElement(label_node, 'CONREF').text = str(picking.origin or "")

            manifest_node = etree.SubElement(print_node, "MANIFEST")
            etree.SubElement(manifest_node, 'CONREF').text = str(picking.origin or "")

            invoice_node = etree.SubElement(print_node, "INVOICE")
            etree.SubElement(invoice_node, 'CONREF').text = str(picking.origin or "")

            etree.SubElement(print_node, 'EMAILTO').text = str(picking_partner_id and picking_partner_id.email or "")
            etree.SubElement(print_node, 'EMAILFROM').text = str(picking_company_id and picking_company_id.email or "")

            etree.SubElement(activity_node, 'SHOW_GROUPCODE').text = ""
            shipment_request_data = str(etree.tostring(shipment_request))
            xml_request = tag + shipment_request_data[2:-1]
            # encode_data = "xml_in=%s" % (xml_request)
            encode_data = "xml_in=%s" % urllib.parse.quote(xml_request)
            try:
                headers = {
                    'SOAPAction': '',
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
                url = "{}/shipping/ship".format(self.company_id and self.company_id.tnt_api_url)
                response_data = requests.request(method="POST", url=url, headers=headers,
                                                 data=encode_data)
                if response_data.status_code in [200, 201]:

                    status = response_data.text
                    complete_code = status.split(':')[1]
                    picking.tnt_complete_code=complete_code
                    status_encode_data = "xml_in=GET_RESULT:%s" % (complete_code)
                    try:
                        headers = {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        }
                        url = "{}/shipping/ship".format(self.company_id and self.company_id.tnt_api_url)
                        response_data_complete = requests.request(method="POST", url=url, headers=headers,
                                                                  data=status_encode_data)
                        if response_data.status_code in [200, 201]:
                            api = Response(response_data_complete.content)
                            response_data = api.dict()
                            _logger.info(response_data)
                            if response_data.get('document') and response_data.get('document').get('CREATE') and response_data.get('document').get('CREATE').get('SUCCESS') == 'Y':
                                CONNUMBER = response_data.get('document').get('CREATE').get('CONNUMBER')
                                shipping_data = {
                                    'exact_price': 0.0,
                                    'tracking_number': CONNUMBER}
                                response += [shipping_data]
                                return response
                            else:
                                raise ValidationError(response_data)
                    except Exception as e:
                        raise ValidationError(e)
            except Exception as e:
                raise ValidationError(e)

