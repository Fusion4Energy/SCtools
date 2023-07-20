# Python Script, API Version = V18
part = GetRootPart()
bodies = part.GetAllBodies()
for b in bodies:
    for f in b.Faces:
        if f.Shape.Geometry.GetType() == Torus:
            sel = Selection.Create(b)
            options = SetColorOptions()
            ColorHelper.SetColor(sel, options, Color.FromArgb(255, 255, 0, 0))
            ColorHelper.SetFillStyle(sel, FillStyle.Opaque)
            break
            