import requests
import re
from bs4 import BeautifulSoup, NavigableString, Tag
import csv
import argparse

sourceUrl = ['https://24.sapo.pt/atualidade/artigos/sns-ja-pagou-mais-de-400-milhoes-de-euros-em-horas-extraordinarias-e-em-prestacoes-de-servico-em-2021',
            'https://24.sapo.pt/desporto/artigos/ainda-com-varios-jogadores-em-isolamento-belenenses-sad-estranha-que-liga-nao-tenha-adiado-jogo-com-o-vizela',
            'https://24.sapo.pt/atualidade/artigos/bimi-o-legume-criado-do-cruzamento-de-brocolos-e-couves-conquistou-os-consumidores-e-tornou-portugal-no-terceiro-maior-produtor-europeu',
            'https://24.sapo.pt/atualidade/artigos/certificado-de-vacinacao-ou-testagem-temporariamente-indisponivel-via-app',
            'https://24.sapo.pt/desporto/artigos/chef-curry-a-cozinhar-mais-um-recorde-de-vitorias-para-os-seus-warriors']

def read_url(url):
    """Read given Url , Returns requests object for page content"""
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Mobile Safari/537.36'}
    s = requests.session()
    response = s.get(url, headers=HEADERS)
    return response.text


def month_converter(month):
    if month.lower() == "janeiro" or month.lower()[0:3] == "jan":
        return "01"
    elif month.lower() == "fevereiro" or month.lower()[0:3] == "fev":
        return "02"
    elif month.lower() == "março" or month.lower()[0:3] == "mar":
        return "03"
    elif month.lower() == "abril" or month.lower()[0:3] == "abr":
        return "04"
    elif month.lower() == "maio" or month.lower()[0:3] == "mai":
        return "05"
    elif month.lower() == "junho" or month.lower()[0:3] == "jun":
        return "06"
    elif month.lower() == "julho" or month.lower()[0:3] == "jul":
        return "07"
    elif month.lower() == "agosto"  or month.lower()[0:3] == "ago":
        return "08"
    elif month.lower() == "setembro" or month.lower()[0:3] == "set":
        return "09"
    elif month.lower() == "outubro" or month.lower()[0:3] == "out":
        return "10"
    elif month.lower() == "novembro" or month.lower()[0:3] == "nov":
        return "11"
    elif month.lower() == "dezembro" or month.lower()[0:3] == "dez":
        return "12"

def to_datetime(story_time):
    #General date/time pattern (long time). https://docs.microsoft.com/en-us/dotnet/standard/base-types/standard-date-and-time-format-strings
    day = story_time.find(attrs={"class": "day"}).text.strip()
    month = story_time.find(attrs={"class": "month"}).text.strip()
    year = story_time.find(attrs={"class": "year"}).text.strip()
    hours = story_time.find(attrs={"class": "time"}).text.strip()
    #print(date)
    ss = '00'
    YYYY , MM ,DD , hh, mm = year, month_converter(month), day, hours.split(':')[0], hours.split(':')[1]
    datetime = f"{YYYY}-{MM}-{DD}T{hh}:{mm}:{ss}"
    return datetime



def article_parser(html_doc, to_datetime):
    soup = BeautifulSoup(html_doc,'html.parser')
    #print(soup)
    label = soup.find(attrs={"class":"category"}).a.text.strip()
    print("LABEL: " + label)
    title = soup.find(attrs={"class":"article-title"}).text.strip()
    print("TITLE: " + title)
    story_lead = soup.find(attrs={"class":"article-excerpt"}).text.strip()
    print("LEAD: " + story_lead)
    story_author = soup.find(attrs={"itemprop":"author"}).text.strip()
    print("AUTHOR: " + story_author)
    story_time = soup.find(attrs={"class":'date'})
    # print(story_time)
    datetime = to_datetime(story_time=story_time)
    print("DATE: " + datetime)
    story_list = []
    for p in soup.find(attrs={'class': 'article-body'}).find(attrs={'class':'content'}):
        if isinstance(p, NavigableString):
            continue
        if isinstance(p,Tag):
            if  (p.text.strip() != '') and ('Publicidade' not in p.text.strip()):
                story_list += [p.text.strip().replace(u'\xa0', u' ')]
        
    story_string = ' '.join(map(str, story_list))
    regex = re.compile(r'[\n\r\t]')
    story_body = regex.sub('', story_string)
  
    #print(story_list)
    # print("BODY: " + story_body)
    return [label,title,story_lead, story_author, datetime , story_body]




def main(outfile):
    with open(outfile, 'w', newline='',encoding="utf-8") as csvfile:
        dataWriter = csv.writer(csvfile, delimiter='/', quoting=csv.QUOTE_MINIMAL)
        for url in sourceUrl:
            html_doc = read_url(url)
            #print(html_doc)
            parsed = article_parser(html_doc, to_datetime=to_datetime)
            parsed += [url]
            dataWriter.writerow(parsed)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scraping articles from https://24.sapo.pt/')
    parser.add_argument('--outfile', required=True, type=str,
                        help='Output file path - where to output the results.')

    args = parser.parse_args()
    main(outfile=args.outfile)
