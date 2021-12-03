from django.http.response import HttpResponse
from django.shortcuts import render
from clean.forms.form import HeaderForm
from clean.models import File, HeaderPreference, Header
from clean.forms.form import FileForm
from django.http import HttpResponseRedirect

import pyspark
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.appName('preferences').getOrCreate()

def frontpage_view(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        
        if form.is_valid():
            file = form.save()
            
            #MAKE HEADER OBJECTS
            df = spark.read.csv(str(file.file_path), header=True)
            header_list = df.columns
            
            for header in header_list:
                # type=dict(df.dtypes)[header] Sets the type to be the columns data type.
                # Only seems to output string though.
                header_object = Header.objects.create(name=header, file=file, selected=True, type=dict(df.dtypes)[header])
                header_definition = HeaderPreference.objects.create(header=header_object)
                header_definition.save()
                header_object.save()

            
            return HttpResponseRedirect("/header-choices/" + str(file.id)) 
    else:
        form = FileForm()
        

    return render(request, "entry.html", {
        "form": form
    })
    

def success_view(request):
    files = File.objects.order_by('id')
    return render(request, "success.html", {
        "files": files
    })
    
    
      
def headerChoice_view(request, pk):
    headers = Header.objects.filter(file_id=pk)
    
    if request.method == 'POST':
        form = HeaderForm(request.POST)
        
        if form.is_valid():
            data = {
                "id": form.cleaned_data['id'],
                "selected": form.cleaned_data['selected'],
                'null_num': form.cleaned_data['null_num'],
                'replace_num': form.cleaned_data['replace_num'],
                'null_string': form.cleaned_data['null_string'],
                'replace_string': form.cleaned_data['replace_string'],
                'null_date': form.cleaned_data['null_date'],
                'replace_date': form.cleaned_data['replace_date'],
            }
            
            print(data)

            header = Header.objects.get(id=data['id'])
            print(header.header_preference.null_choice_string)
            header.selected = data['selected']
            header.header_preference.null_choice_num = data['null_num'] if data['null_num'] != '' else None
            header.header_preference.null_choice_string = data['null_string'] if data['null_string'] != '' else None
            header.header_preference.null_choice_date = data['null_date'] if data['null_date'] != '' else None
            header.header_preference.save()
            header.save()
            header = Header.objects.get(id=data['id'])
 
            
            
            return HttpResponseRedirect("/header-choices/" + str(pk)) 
    else:
        form = HeaderForm()
    
    return render(request, "header_choices.html", {
        "form": form,
        "header_list": headers,
        "file_id": pk
    })

    
def help_view(request):
    return render(request, "help.html")

