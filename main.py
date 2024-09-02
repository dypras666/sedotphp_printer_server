import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QTabWidget, QLineEdit, 
                             QTextEdit, QFormLayout, QSpinBox, QMessageBox, QTextBrowser)
from PyQt5.QtCore import Qt
from receipt_template import ReceiptTemplate, PrinterManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.receipt_template = ReceiptTemplate()
        self.printer_manager = PrinterManager()
        self.load_config()
        self.initUI()

    def load_config(self):
        try:
            with open('mosys.json', 'r') as f:
                config = json.load(f)
                self.active_printer = config.get('active_printer')
                if self.active_printer:
                    self.printer_manager.set_printer(self.active_printer)
        except FileNotFoundError:
            self.active_printer = None
            print("mosys.json not found")
        except json.JSONDecodeError:
            self.active_printer = None
            print("Invalid JSON in mosys.json")

    def initUI(self):
        self.setWindowTitle('Mosys Printer')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self.createServerInfoTab(), "Server Info")
        tabs.addTab(self.createPrinterTab(), "Printer Settings")
        tabs.addTab(self.createTemplateTab(), "Template Designer")
        tabs.addTab(self.createTestPrintTab(), "Test Print")

        layout.addWidget(tabs)

    def createServerInfoTab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        info_text = QTextBrowser()
        info_text.setOpenExternalLinks(True)
        info_text.setHtml("""
        <h2>Server Information</h2>
        <p>Developed by Kurniawan <br> Instagram : <a href="https://instagram.com/sedotphp">@sedotphp</a></p>
        <p>The server is running at: <a href="http://localhost:1717">http://localhost:1717</a></p>
        <h3>Available Endpoints:</h3>
        <ul>
            <li><strong>GET /printers</strong>: Get a list of available printers</li>
            <li><strong>POST /set_printer</strong>: Set the active printer</li>
            <li><strong>POST /print</strong>: Print a receipt</li>
            <li><strong>POST /update_template</strong>: Update the receipt template</li>
        </ul>
        <h3>How to use /print endpoint:</h3>
        <p>Send a POST request to <code>http://localhost:1717/print</code> with the following form-data:</p>
        <ul>
            <li><code>nama_toko</code>: Store name (string)</li>
            <li><code>alamat_toko</code>: Store address (string)</li>
            <li><code>no_hp</code>: Store phone number (string)</li>
            <li><code>nama_kasir</code>: Cashier name (string)</li>
            <li><code>code</code>: Purchase code (string)</li>
            <li><code>tanggal</code>: Transaction date and time (string, format: "YYYY-MM-DD HH:MM:SS")</li>
            <li><code>items</code>: List of purchased items (JSON string array)</li>
            <li><code>notes</code>: Additional notes (string, optional)</li>
        </ul>
        <p>Example of <code>items</code> structure:</p>
        <pre>
[
  {
    "nama_produk": "Product A",
    "qty": 2,
    "satuan": "pcs",
    "harga": 10000,
    "diskon": 1000,
    "total_harga": 19000
  },
  {
    "nama_produk": "Product B",
    "qty": 1,
    "satuan": "pcs",
    "harga": 15000,
    "diskon": 0,
    "total_harga": 15000
  }
]
        </pre>
        """)
        layout.addWidget(info_text)

        widget.setLayout(layout)
        return widget

    def createPrinterTab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Printer selection
        printer_layout = QHBoxLayout()
        self.printer_combo = QComboBox()
        self.updatePrinterList()
        printer_layout.addWidget(QLabel("Select Printer:"))
        printer_layout.addWidget(self.printer_combo)
        set_printer_btn = QPushButton("Set Printer")
        set_printer_btn.clicked.connect(self.setPrinter)
        printer_layout.addWidget(set_printer_btn)
        layout.addLayout(printer_layout)

        # Show active printer
        self.active_printer_label = QLabel(f"Active Printer: {self.active_printer or 'None'}")
        layout.addWidget(self.active_printer_label)

        # Refresh printer list button
        refresh_btn = QPushButton("Refresh Printer List")
        refresh_btn.clicked.connect(self.updatePrinterList)
        layout.addWidget(refresh_btn)

        widget.setLayout(layout)
        return widget

    def createTemplateTab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.paper_size = QComboBox()
        self.paper_size.addItems(['58mm', '80mm'])
        self.paper_size.setCurrentText(self.receipt_template.template['paper_size'])
        form_layout.addRow("Paper Size:", self.paper_size)

        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(self.receipt_template.template['font_size'])
        form_layout.addRow("Font Size:", self.font_size)

        self.header_format = QTextEdit()
        self.header_format.setPlainText(self.receipt_template.template['header_format'])
        form_layout.addRow("Header Format:", self.header_format)

        self.cashier_format = QLineEdit(self.receipt_template.template['cashier_format'])
        form_layout.addRow("Cashier Format:", self.cashier_format)

        self.code_format = QLineEdit(self.receipt_template.template['code_format'])
        form_layout.addRow("Code Format:", self.code_format)

        self.date_format = QLineEdit(self.receipt_template.template['date_format'])
        form_layout.addRow("Date Format:", self.date_format)

        self.item_format = QTextEdit()
        self.item_format.setPlainText(self.receipt_template.template['item_format'])
        form_layout.addRow("Item Format:", self.item_format)

        self.summary_format = QTextEdit()
        self.summary_format.setPlainText(self.receipt_template.template['summary_format'])
        form_layout.addRow("Summary Format:", self.summary_format)

        self.footer_format = QTextEdit()
        self.footer_format.setPlainText(self.receipt_template.template['footer_format'])
        form_layout.addRow("Footer Format:", self.footer_format)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Template")
        save_btn.clicked.connect(self.saveTemplate)
        button_layout.addWidget(save_btn)

        test_template_btn = QPushButton("Test Template")
        test_template_btn.clicked.connect(self.testTemplate)
        button_layout.addWidget(test_template_btn)

        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def createTestPrintTab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.test_print_text = QTextEdit()
        self.test_print_text.setPlainText("Test print content")
        layout.addWidget(QLabel("Enter text to print:"))
        layout.addWidget(self.test_print_text)

        print_btn = QPushButton("Print Test")
        print_btn.clicked.connect(self.printTest)
        layout.addWidget(print_btn)

        widget.setLayout(layout)
        return widget

    def updatePrinterList(self):
        self.printer_combo.clear()
        printers = self.printer_manager.get_printers()
        self.printer_combo.addItems(printers)
        
        # Set the active printer in the combo box
        if self.active_printer and self.active_printer in printers:
            index = self.printer_combo.findText(self.active_printer)
            if index >= 0:
                self.printer_combo.setCurrentIndex(index)

    def setPrinter(self):
        printer_name = self.printer_combo.currentText()
        if self.printer_manager.set_printer(printer_name):
            self.active_printer = printer_name
            self.active_printer_label.setText(f"Active Printer: {self.active_printer}")
            self.updateConfig()
            QMessageBox.information(self, "Printer Set", f"Active printer set to: {printer_name}")
        else:
            QMessageBox.warning(self, "Error", "Failed to set printer")

    def updateConfig(self):
        config = {"active_printer": self.active_printer}
        with open('mosys.json', 'w') as f:
            json.dump(config, f)

    def saveTemplate(self):
        new_template = {
            'paper_size': self.paper_size.currentText(),
            'font_size': self.font_size.value(),
            'header_format': self.header_format.toPlainText(),
            'cashier_format': self.cashier_format.text(),
            'code_format': self.code_format.text(),
            'date_format': self.date_format.text(),
            'item_format': self.item_format.toPlainText(),
            'summary_format': self.summary_format.toPlainText(),
            'footer_format': self.footer_format.toPlainText()
        }
        self.receipt_template.update_template(**new_template)
        QMessageBox.information(self, "Template Saved", "Receipt template has been updated and saved")

    def testTemplate(self):
        self.saveTemplate()

        test_data = {
            'nama_toko': 'Toko ABC',
            'alamat_toko': 'Jl. Contoh No. 123',
            'no_hp': '08123456789',
            'nama_kasir': 'John Doe',
            'code': '12121211',
            'tanggal': '2024-09-02 15:30:00',
            'items': [
                {
                    'nama_produk': 'Produk A',
                    'qty': 2,
                    'satuan': 'pcs',
                    'harga': 10000,
                    'diskon': 1000,
                    'total_harga': 19000
                },
                {
                    'nama_produk': 'Produk B',
                    'qty': 1,
                    'satuan': 'pcs',
                    'harga': 15000,
                    'diskon': 0,
                    'total_harga': 15000
                }
            ],
            'notes': 'Terima kasih telah berbelanja!'
        }

        receipt_text = self.receipt_template.generate_receipt(test_data)

        if not self.printer_manager.active_printer:
            QMessageBox.warning(self, "No Printer", "Please select a printer first")
            return

        result, status_code = self.printer_manager.print_text(receipt_text)
        if status_code == 200:
            QMessageBox.information(self, "Print Success", "Test template printed successfully")
        else:
            QMessageBox.warning(self, "Print Error", f"Failed to print: {result}")

    def printTest(self):
        if not self.printer_manager.active_printer:
            QMessageBox.warning(self, "No Printer", "No active printer selected. Please select a printer first.")
            return

        text = self.test_print_text.toPlainText()
        result, status_code = self.printer_manager.print_text(text)
        if status_code == 200:
            QMessageBox.information(self, "Print Success", "Test print sent successfully")
        else:
            QMessageBox.warning(self, "Print Error", f"Failed to print: {result}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())