from django.forms import ModelForm, TextInput
from auctions.models import Listing



class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = '__all__'
        exclude = ['owner_id', 'winner_id', 'is_active']
        widgets = {            
            'title': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 400px;',
                
                }),
             'description': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 400px; height : 300px;', 
              
                }),
            'image': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'Must be URL for PNG/JPG/JPEG File (optional)'
                }),
            
        }


        #form = NewTaskForm(request.POST)
       # if form.is_valid():

        # If the form is invalid, re-render the page with existing information.
       #     return render(request, "tasks/add.html", {
      #          "form": form
       #     })
