# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 15:39:56 2020

@author: cubial
"""
from docx import Document
from docxtpl import DocxTemplate, InlineImage
from docxcompose.composer import Composer
from docx.shared import Cm
import pandas as pd
from tqdm import tqdm 
import re
import os

BOM_file = 'TOKAMAK_COMPLEX_with_MATERIALS.csv'
template_file = 'TEMPLATE.docx'
Original_pictures = 'Original_Pictures'
Simplified_pictures = 'Simplified_Pictures'

class ATLAS():
    '''
    This class represents the whole ATLAS that will contain all the components.
    The ATLAS is generated as a merging of documents where every document is 
    a modification of the one-page document used as TEMPLATE.
    '''
    def __init__(self,df):
        
        doc = Document()
        self.doc = Composer(doc)
        self.df  = df
        self.names = [] #list of part names that already appeared in the ATLAS

        
        
    def write_page(self,i):
        '''
        Creates a docx that consists on the template page fulfilled with a 
        component info.
        '''
        df_row      = self.df.iloc[i]
        name = name_from_df(df_row)

        while name in self.names: # if the name exsts add a counter at the end
            if name[-1] != ')':
                name = name + '(2)'
            else:
                c = int(re.search('(\d+)\)$',name).group(1))
                c = c+1
                name = re.sub('(\d+)\)$',str(c)+')',name)
        self.names.append(name)
        
        page = DocxTemplate("TEMPLATE.docx")
        if str(df_row['CELL IDs']) == 'nan':
            context = {
            'name'        : name,
            'enovia_code' : enovia_code_from_df(df_row),
            'material'    : 'ASSEMBLY',
            'density'     : 'ASSEMBLY',
            'dcf'         : 'ASSEMBLY',
            'mass'        : 'ASSEMBLY',
            'comment'     : 'N/A'
                   }
        else:
            context = {
            'name'        : name,
            'enovia_code' : enovia_code_from_df(df_row),
            'material'    : df_row['MATERIAL'],
            'density'     : df_row['DENSITY [g/cm3]'],
            'dcf'         : "{:.3f}".format(df_row['DCF=ORG/STOCH']), 
            'mass'        : "{:.2f}".format(float(df_row['DENSITY [g/cm3]'])*float(df_row['ORIGINAL VOLUME [cm3]'])), #'mass'        : df_row['MASS [g]'],
            'comment'     : 'N/A'
                       }
        pic_ori = InlineImage(page, Original_pictures+'\\'+str(i+2)+'.jpg',width=Cm(11))
        context['pic_ori'] = pic_ori
        
        pic_sim = Simplified_pictures+'\\'+str(i+2)+'.jpg'
        if df_row['CELL IDs'] == 'DELETED' or os.path.exists(pic_sim)==False:
            pic_sim = '              DELETED'
            context['dcf'] = 'N/A'
            context['comment'] = 'Deleted component'
        else:
            pic_sim = InlineImage(page, pic_sim, width=Cm(11))
        context['pic_sim'] = pic_sim
        page.render(context)
        #page.add_page_break()
        #page.save(enovia_code_from_df(df_row)+'.docx')
        return page
        


def enovia_code_from_df(df_row):
    names = list(df_row)
    names = names[::-1]
    for n in names:
        try: 
            return re.search('\#.{6}$',n).group()[1:]
        except: pass
    return 'N/A'

def name_from_df(df_row):
    maxLevel = 'Level 1'
    for k in df_row.keys():
        if 'Level' in k:
            if int(re.findall('\d+',k)[0]) > int(re.findall('\d+',maxLevel)[0]):
                if df_row[k] != '-':
                    maxLevel = k
    return df_row[maxLevel]
    
    
if BOM_file[-3:]=='csv':
    df = pd.read_csv(BOM_file)
else:
    df = pd.read_excel(BOM_file)

report = ATLAS(df)

bar = tqdm(unit=' pages',desc=' Writing',total=df.shape[0])
for i in report.df.index:
    bar.update()
    # if report.df['Level 4'][i] == '-':
    #     page = report.write_page(i)
    #     report.doc.append(page)
    page = report.write_page(i)
    report.doc.append(page)

    
bar.close()


report.doc.save('ATLAS.docx')



# This bit is to be used if we want to divide the ATLAS between documents of
# no more than 300 pages in case the ATLAS is too big to be handled properly.
    
#pages = []
#report = ATLAS(df)
#bar = tqdm(unit=' pages',desc=' Writing',total=df.shape[0])
#for i in report.df.index:
#    page = report.write_page(i)
#    pages.append(page)
#    #report.doc.append(page)
#    bar.update()
#bar.close()
#
#bar = tqdm(unit=' pages',desc=' Merging',total=df.shape[0])
#r=0
#reports = {r:ATLAS(df)}
#c = 0
#while len(pages)!=0:
#    c = c + 1 
#    reports[r].doc.append(pages.pop(0))
#    if c == 300:
#        c = 0
#        r = r+1
#        reports[r] = ATLAS(df)
#    bar.update()
#
#bar.close()
#
#bar = tqdm(unit=' docs',desc=' Saving',total=r+1)
#for key in list(reports.keys()):
#    reports[key].doc.save(str(key+1)+'-ATLAS.docx')
#    bar.update()
#bar.close()








