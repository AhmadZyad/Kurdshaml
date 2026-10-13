import json
import urllib.parse
from http.server import BaseHTTPRequestHandler
from deep_translator import GoogleTranslator

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # وەرگرتنی وشە و ژمارەی لاپەڕە لە بەستەرەکەوە
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        search_query = query_components.get("q", [""])[0]
        page = int(query_components.get("page", ["1"])[0])
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if not search_query:
            self.wfile.write(json.dumps({"error": "تکایە وشەیەک بنووسە بۆ گەڕان"}).encode('utf-8'))
            return
            
        try:
            # ئامادەکردنی وەرگێڕانی سۆرانی
            translator = GoogleTranslator(source='ar', target='ckb')
            results = []
            has_next = False
            
            # دانانی ١٠ ئەنجام بۆ هەر جارێک کە فرۆنتئەندەکە داوای دەکات
            items_per_page = 10
            max_total_results = 120 # دەتوانیت تا ١٠٠٠ زیادی بکەیت!
            
            start_index = (page - 1) * items_per_page + 1
            end_index = start_index + items_per_page
            
            if start_index <= max_total_results:
                for i in range(start_index, end_index):
                    if i > max_total_results:
                        break
                        
                    # دروستکردنی دەقی عەرەبی درێژ وەکو شێوازی مەکتەبەی شامیلە
                    arabic_text = f"وقد جاء في تفصيل باب ( {search_query} ) في الصفحة رقم {i} ما يفيد الباحث. وهذا النص مأخوذ كنموذج حي ومباشر لتوضيح كيفية استخراج النصوص الطويلة والمعقدة من المكتبة الشاملة وترجمتها فورا."
                    
                    # پرۆسەی وەرگێڕان
                    try:
                        kurdish_text = translator.translate(arabic_text)
                    except:
                        kurdish_text = "ببورە، هەڵەیەک لە وەرگێڕاندا ڕوویدا."
                        
                    results.append({
                        "book": f"الموسوعة الفقهية الكبرى - المجلد { (i // 15) + 1 }",
                        "page": str(120 + i),
                        "arabic_text": arabic_text,
                        "kurdish_text": kurdish_text
                    })
                
                # ئەگەر هێشتا نەگەیشتووینەتە ١٢٠ ئەنجامەکە، پێی بڵێ با لاپەڕەی دواتر بهێنێت
                if end_index <= max_total_results:
                    has_next = True
            
            response_data = {
                "results": results,
                "has_next": has_next,
                "page": page,
                "total_fetched": len(results)
            }
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.wfile.write(json.dumps({"error": f"هەڵەیەک لە سێرڤەر ڕوویدا: {str(e)}"}).encode('utf-8'))
