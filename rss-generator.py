class ExtendedRSSFeed(feedgenerator.Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    """
    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs
        
    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)
        handler.addQuickElement(u'content:encoded', item['content_encoded'])



class LatestNewsFeed(Feed):

    feed_type = ExtendedRSSFeed  
    title = None
    description = None
    link='/feeds/'
    site = None
    rss_category = None
    feed_type.content_type = 'application/xml; charset=utf-8'
    full_path = None

    def get_object(self, request, rss_cat):
        self.site = get_current_site(request)
        url_scheme =str(request.build_absolute_uri()).split('//')[0]
        url_domain = str(self.site.domain)
        self.full_path = f'{url_scheme}://{url_domain}'
        if str(self.site) == settings.PANCHJANYA_DOMAIAN:
            self.title = str('पांचजन्य - बात भारत की  ')
            self.description = str('वर्ष 1948 से लगातार राष्ट्रवाद की अलख जगा रहा है। भारतीय मूल्यों और सांस्कृतिक चेतना को मंच मिले औ राष्ट्रीय लक्ष्यों का स्मरण कराते रहना पाञ्चजन्य का ध्येय है।')
        else:
            self.title = str('Organiser - The Voice of the nation')
            self.description = str('Organiser - The oldest and most widely circulated nationalist English weekly of Bharat. Spreading Cultural Nationalist Views which goes beyond News.')
        self.rss_category = str(rss_cat)
        return

    def items(self):
        filter_data={} 
        if str(self.site) == settings.PANCHJANYA_DOMAIAN:
            filter_data['is_Panchjanya'] = True
        else:
            filter_data['is_Organizer'] = True
        if self.rss_category != None:
            return News.objects.filter(**filter_data).filter(categoryName__name_en=self.rss_category).order_by("-date")[:10]
        return Http404

    def item_extra_kwargs(self, item):
        return {'content_encoded': self.item_content_encoded(item)}


    def item_title(self, item):
        return item.title

    def item_description(self,item):
        return strip_tags(truncatewords(html.unescape(item.content), 100))

    def item_link(self,item):
        return item.get_absolute_url()

    def item_author_name(self, item):
        pass
        # return 'Webdesk' if item.uploaded_by.name is None else  item.uploaded_by.name
    
    def item_pubdate(self, item):
        return item.updated_at or item.date


    def item_content_encoded(self, item):
        html_content_file = '''
            <![CDATA[
        <html lang="en" prefix="op: http://media.facebook.com/op#">
          <head>
            <meta charset="utf-8">
            <link rel="canonical" href='''+f'"{self.full_path}{item.get_absolute_url()}">'+'''<meta property="op:markup_version" content="v1.0">
          </head>
          <body>
            <article>
              <header>'''+item.title+'''
                
              </header>

              '''+strip_tags(truncatewords(html.unescape(item.content),100))+'''

            </article>
          </body>
        </html>
        ]]>
        '''
        return html_content_file
        
class Rss(View):
    def get(self, request):
        filter_dict = {}
        current_site = request.get_host()
        if current_site == settings.PANCHJANYA_DOMAIAN:
            filter_dict["is_Panchjanya"]=True
            temp="Pauthenticate/rss.html"
        else:
            filter_dict['is_Organizer'] = True
            temp="authenticate/rss.html"
        category_list = Category.objects.filter(**filter_dict)
        top_category_list = News.objects.active().filter(**filter_dict).filter(categoryName=4).order_by("-id")[:3]
        pan_top_category_list = News.objects.active().filter(**filter_dict).filter(categoryName=14).order_by("-id")[:3]
        context={
            "all_category": category_list,
            "top_news":top_category_list,
            "pan_top_news":pan_top_category_list,

        }
        return render(request, temp,context)

