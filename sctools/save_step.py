# Python Script, API Version = V18
# This script saves the model as a step file
# that will mantain cellID order in SuperMC.
part = GetRootPart()
bodies = part.GetAllBodies()
# To avoid surfaces
bodies = [b for b in bodies if b.Shape.Volume>0.0]
#Copy.ToClipboard(Selection.Create(bodies))
DocumentHelper.CreateNewDocument()
for i in range(len(bodies)):
    c = ComponentHelper.CreateAtRoot('Component_'+str(i+1))
    ComponentHelper.SetActive(Selection.Create(c))
    sel = Selection.Create(bodies[i])
    Copy.ToClipboard(sel)
    Paste.FromClipboard()

path = part.Document.Path[:-5]+'stp'
options = ExportOptions.Create()
DocumentSave.Execute(path, options)
DocumentHelper.CloseDocument()
