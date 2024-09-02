import json
from datetime import datetime
from flask import Flask, request, jsonify
import win32print
import win32con
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ReceiptTemplate:
    def __init__(self):
        self.template = {
            'paper_size': '80mm',
            'font_size': 12,
            'header_format': '{nama_toko}\n{alamat_toko}\nTelp: {no_hp}',
            'cashier_format': 'Kasir: {nama_kasir}',
            'date_format': 'Tanggal: {tanggal}',
            'item_format': '{nama_produk:<20} {qty:>3} {satuan:<3} x {harga:>7} - {diskon:>5} = {total_harga:>8}',
            'summary_format': 'Total Item: {total_item}\nTotal Diskon: {total_diskon}\nTotal Harga: {total_harga}',
            'footer_format': 'Notes: {notes}'
        }
        self.load_template()

    def load_template(self):
        try:
            with open('receipt_template.json', 'r') as f:
                saved_template = json.load(f)
                self.template.update(saved_template)
        except FileNotFoundError:
            self.save_template()

    def save_template(self):
        with open('receipt_template.json', 'w') as f:
            json.dump(self.template, f, indent=2)

    def update_template(self, **kwargs):
        self.template.update(kwargs)
        self.save_template()

    def generate_receipt(self, data):
        receipt = []

        # Header
        receipt.append(self.template['header_format'].format(
            nama_toko=data.get('nama_toko', ''),
            alamat_toko=data.get('alamat_toko', ''),
            no_hp=data.get('no_hp', '')
        ))

        # Cashier and Date
        receipt.append(self.template['cashier_format'].format(nama_kasir=data.get('nama_kasir', '')))
        receipt.append(self.template['date_format'].format(tanggal=data.get('tanggal', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))))

        # Items
        receipt.append('\n' + '-' * 40)
        for item in data.get('items', []):
            receipt.append(self.template['item_format'].format(**item))
        receipt.append('-' * 40)

        # Summary
        receipt.append(self.template['summary_format'].format(
            total_item=sum(item['qty'] for item in data.get('items', [])),
            total_diskon=sum(item['diskon'] for item in data.get('items', [])),
            total_harga=sum(item['total_harga'] for item in data.get('items', []))
        ))

        # Footer
        if 'notes' in data:
            receipt.append('\n' + self.template['footer_format'].format(notes=data['notes']))

        return '\n'.join(receipt)

class PrinterManager:
    def __init__(self):
        self.active_printer = None
        self.load_printer_from_config()

    def load_printer_from_config(self):
        try:
            with open('mosys.json', 'r') as f:
                config = json.load(f)
                printer_name = config.get('active_printer')
                if printer_name:
                    if self.set_printer(printer_name):
                        logging.info(f"Printer loaded from config: {printer_name}")
                    else:
                        logging.warning(f"Printer '{printer_name}' from config not found or couldn't be set")
                else:
                    logging.warning("No active_printer found in mosys.json")
        except FileNotFoundError:
            logging.warning("mosys.json not found")
        except json.JSONDecodeError:
            logging.error("Invalid JSON in mosys.json")

    def get_printers(self):
        return [printer[2] for printer in win32print.EnumPrinters(2)]

    def set_printer(self, printer_name):
        if printer_name in self.get_printers():
            self.active_printer = printer_name
            return True
        logging.warning(f"Printer '{printer_name}' not found")
        return False

    def print_text(self, text):
        if not self.active_printer:
            return "No active printer selected", 400

        try:
            hPrinter = win32print.OpenPrinter(self.active_printer)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Print Job", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)
                    
                    if isinstance(text, str):
                        text = text.encode('utf-8', errors='replace')
                    
                    commands = b"\x1B\x40"  # Initialize printer
                    commands += text
                    commands += b"\x0A\x0D"  # New line
                    commands += b"\x1D\x56\x41\x03"  # Cut paper
                    
                    win32print.WritePrinter(hPrinter, commands)
                    
                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
            return "Print job sent successfully", 200
        except Exception as e:
            error_msg = f"Error printing: {str(e)}"
            logging.error(error_msg)
            return error_msg, 500

receipt_template = ReceiptTemplate()
printer_manager = PrinterManager()

@app.route('/printers', methods=['GET'])
def get_printers():
    return jsonify(printer_manager.get_printers())

@app.route('/set_printer', methods=['POST'])
def set_printer():
    printer_name = request.json.get('printer_name')
    if printer_manager.set_printer(printer_name):
        return jsonify({"message": f"Printer set to {printer_name}"}), 200
    else:
        return jsonify({"error": "Invalid printer name"}), 400

@app.route('/print', methods=['POST'])
def print_receipt():
    if not printer_manager.active_printer:
        return jsonify({"error": "No active printer selected. Check mosys.json configuration."}), 400
    
    try:
        data = {
            'nama_toko': request.form.get('nama_toko'),
            'alamat_toko': request.form.get('alamat_toko'),
            'no_hp': request.form.get('no_hp'),
            'nama_kasir': request.form.get('nama_kasir'),
            'tanggal': request.form.get('tanggal'),
            'items': json.loads(request.form.get('items', '[]')),
            'notes': request.form.get('notes')
        }
        
        if not data['nama_toko']:
            return jsonify({"error": "No data provided"}), 400
        
        receipt_text = receipt_template.generate_receipt(data)
        result, status_code = printer_manager.print_text(receipt_text)
        return jsonify({"message": result}), status_code
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON in 'items' field"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_template', methods=['POST'])
def update_template():
    new_template = request.json
    if not new_template:
        return jsonify({"error": "No template data provided"}), 400
    
    try:
        receipt_template.update_template(**new_template)
        return jsonify({"message": "Template updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update template: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1717)