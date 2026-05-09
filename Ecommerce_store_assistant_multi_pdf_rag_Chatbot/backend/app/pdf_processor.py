# backend/app/pdf_processor.py
import os
from typing import List, Dict
import PyPDF2

class PDFProcessor:
    """Process PDF files for e-commerce content"""
    
    def __init__(self):
        self.pdf_dir = os.path.join(os.path.dirname(__file__), "data", "pdfs")
    
    def process_all_pdfs(self) -> List[Dict]:
        """Process all PDFs in the directory using PyPDF2"""
        all_chunks = []
        
        if not os.path.exists(self.pdf_dir):
            print(f"📁 PDF directory not found: {self.pdf_dir}")
            return all_chunks
        
        print(f"\n📁 Scanning PDF directory: {self.pdf_dir}")
        
        for pdf_file in os.listdir(self.pdf_dir):
            if pdf_file.endswith('.pdf'):
                print(f"📄 Processing: {pdf_file}")
                pdf_path = os.path.join(self.pdf_dir, pdf_file)
                
                try:
                    content = self._extract_text(pdf_path)
                    
                    if content and len(content.strip()) > 10:
                        all_chunks.append({
                            'text': content,
                            'metadata': {
                                'source': pdf_file,
                                'type': pdf_file.replace('.pdf', '')
                            }
                        })
                        print(f"   ✓ Extracted {len(content)} characters from {pdf_file}")
                    else:
                        print(f"   ⚠️ No text extracted from {pdf_file}, using fallback")
                        content = self._get_fallback_content(pdf_file)
                        all_chunks.append({
                            'text': content,
                            'metadata': {
                                'source': pdf_file,
                                'type': pdf_file.replace('.pdf', '')
                            }
                        })
                except Exception as e:
                    print(f"   ❌ Error processing {pdf_file}: {e}")
                    # Still add fallback so the bot has some info
                    content = self._get_fallback_content(pdf_file)
                    all_chunks.append({
                        'text': content,
                        'metadata': {
                            'source': pdf_file,
                            'type': pdf_file.replace('.pdf', '')
                        }
                    })
        
        return all_chunks
    
    def _extract_text(self, pdf_path: str) -> str:
        """Extract text from a single PDF file"""
        text = ""
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def _get_fallback_content(self, filename: str) -> str:
        """Get fallback content based on filename if extraction fails"""
        
        fallback_map = {
            "products.pdf": """
TechStore Pro Products:
iPhone 15 Pro - $999
- Colors: Natural Titanium, Blue Titanium, White Titanium, Black Titanium
- Storage: 128GB, 256GB, 512GB, 1TB
- Features: A17 Pro chip, 48MP camera, USB-C, Action button

MacBook Pro M3 - $1,599
- Specs: M3 chip, 8GB RAM, 512GB SSD
- Colors: Space Gray, Silver
- Battery: 22 hours

AirPods Pro 2 - $199
- Active Noise Cancellation, Transparency mode
- Battery: 6 hours, 30 hours with case

Samsung Galaxy S24 Ultra - $1,199
- 200MP camera, S Pen included, 7 years updates
- Battery: 5,000mAh, 45W charging
""",
            "faq.pdf": """
Frequently Asked Questions:
Q: How do I track my order?
A: Use tracking link in your confirmation email or visit "My Orders"

Q: Can I cancel my order?
A: Within 1 hour of placing order, contact support. After that, returns only.

Q: Do you price match?
A: Yes! We match Amazon, Best Buy, and Walmart prices.

Q: What payment methods do you accept?
A: Credit cards, PayPal, Apple Pay, Google Pay, Klarna, Affirm

Q: What warranty do you offer?
A: 1 year manufacturer warranty on all products.

Q: Do you offer technical support?
A: Yes, free setup assistance and troubleshooting guides included.
""",
            "returns.pdf": """
Return & Refund Policy:
- 30-day return window from delivery date
- Items must be in original condition with packaging
- Free returns for defective products or wrong items
- Refund processed within 3-5 business days

Non-returnable items:
- Gift cards, software, opened headphones

Refund amounts:
- Unopened: 100% refund
- Opened but unused: 85% refund
- Missing packaging: 50% refund
""",
            "shipping.pdf": """
Shipping Information:
Standard Shipping (5-7 days): Free on $50+, else $5.99
Express Shipping (2-3 days): $12.99 flat rate
Next-Day Delivery: $19.99 (order by 2 PM)

International Shipping:
- Canada: $15.99 (7-10 days)
- UK/Europe: $24.99 (10-14 days)
- Australia/Asia: $29.99 (14-21 days)

Free shipping on all orders over $50!
""",
            "promotions.pdf": """
Current Deals & Promotions:
Apple Deals:
- iPhone 15 Pro: Save $100 + free AirPods
- MacBook Air M2: $899 (regular $1,099)
- iPad 10th Gen: $399 with free Pencil

Samsung Offers:
- Galaxy S24 Ultra: Trade-in any phone, get $800 off
- Galaxy Buds2 Pro: $149 (save $80)

Student Discount: 15% off with .edu email

Clearance: Up to 60% off select items
"""
        }
        
        return fallback_map.get(filename, f"Content from {filename}")
