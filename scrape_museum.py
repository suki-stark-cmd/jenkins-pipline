import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import re
import urllib3
# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Base URL of the website
base_url = "https://museumsofindia.gov.in/repository"
# Set to keep track of visited URLs
visited_urls = set()
# PDF generation class
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Museum Data', 0, 1, 'C')
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        # Encode title using utf-8 and replace problematic characters
        title = title.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 10, title, 0, 1, 'L')
    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        # Encode body using utf-8 and replace problematic characters
        body = body.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 10, body)
    def add_chapter(self, title, body):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(body)
# Function to clean up and get textual content from a tag
def extract_text(soup):
    paragraphs = soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    content = ""
    for paragraph in paragraphs:
        text = paragraph.get_text(strip=True)
        if text:
            content += text + "\n\n"
    return content
# Function to recursively scrape data and generate PDF
def scrape_page(url, pdf):
    # Check if URL is already visited
    if url in visited_urls:
        return
    # Mark this URL as visited
    visited_urls.add(url)
    # Send a GET request to the URL
    response = requests.get(url, verify=False)
    # If the request is successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract the page title
        title_tag = soup.find('title')
        page_title = title_tag.text.strip() if title_tag else 'No title'
        # Extract textual content from the page
        page_content = extract_text(soup)
        # Add the content to the PDF
        pdf.add_chapter(page_title, page_content)
        print(f"Scraped: {page_title} - {url}")
        # Find all the links on the page
        links = soup.find_all('a', href=True)
        # Filter only internal links within the museum repository
        internal_links = [link['href'] for link in links if re.match(r'^/repository', link['href'])]
        # Recursively scrape each internal link
        for link in internal_links:
            full_link = f"https://museumsofindia.gov.in{link}"
            scrape_page(full_link, pdf)
    else:
        print(f"Failed to access {url} (Status code: {response.status_code})")
# Initialize PDF object
pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
# Start scraping from the base URL
scrape_page(base_url, pdf)
# Save the PDF file
pdf.output(r"C:\Users\sukic\Downloads\museum_full_data.pdf")
print("Scraping complete. Data saved to PDF.")