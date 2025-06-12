using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;


namespace Revit_Addin_Development
{

    [TransactionAttribute(TransactionMode.Manual)]
    [RegenerationAttribute(RegenerationOption.Manual)]
    public class MA : IExternalCommand
    {
        public ICollection<ElementId> GetElementIds(Document doc, List<string> IFC_GUIDs)
        {
            // quick filter
            ElementCategoryFilter floorFilter = new ElementCategoryFilter(BuiltInCategory.OST_Floors);
            ElementCategoryFilter wallFilter = new ElementCategoryFilter(BuiltInCategory.OST_Walls);
            ElementCategoryFilter doorFilter = new ElementCategoryFilter(BuiltInCategory.OST_Doors);
            ElementCategoryFilter roomFilter = new ElementCategoryFilter(BuiltInCategory.OST_Rooms);
            ElementCategoryFilter furnitureFilter = new ElementCategoryFilter(BuiltInCategory.OST_Furniture);
            ElementCategoryFilter stairsFilter = new ElementCategoryFilter(BuiltInCategory.OST_Stairs);
            ElementCategoryFilter loadedFamilyFilter = new ElementCategoryFilter(BuiltInCategory.OST_GenericModel);


            List<ElementFilter> quickFilterSet = new List<ElementFilter>
            {
                floorFilter,
                wallFilter,
                doorFilter,
                roomFilter,
                furnitureFilter,
                stairsFilter,
                loadedFamilyFilter
            };

            // slow filter: element parameter filter
            BuiltInParameter parameter = BuiltInParameter.IFC_GUID;
            ParameterValueProvider provider = new ParameterValueProvider(new ElementId(parameter));
            FilterStringRuleEvaluator evaluator = new FilterStringEquals();

            List<ElementFilter> slowFilterSet = new List<ElementFilter>();
            foreach (string IFC_GUID in IFC_GUIDs)
            {
                string ruleValue = IFC_GUID;
                FilterRule rule = new FilterStringRule(provider, evaluator, ruleValue);
                ElementParameterFilter slowFilter = new ElementParameterFilter(rule);
                slowFilterSet.Add(slowFilter);
            }

            // logical filter : or filter
            LogicalOrFilter logicalOrFilter_quick = new LogicalOrFilter(quickFilterSet);
            LogicalOrFilter logicalOrFilter_slow = new LogicalOrFilter(slowFilterSet);

            // Collect Elements
            FilteredElementCollector collector = new FilteredElementCollector(doc).WherePasses(logicalOrFilter_quick).WherePasses(logicalOrFilter_slow);

            // get ElementIds 
            /*List<Autodesk.Revit.DB.Element> instances = collector.ToList<Autodesk.Revit.DB.Element>(); */
            ICollection<ElementId> instanceIds = collector.ToElementIds();
            return instanceIds;
        }

        public View GetSourceView(Document doc, ElementId elementId)
        {
            Element element = doc.GetElement(elementId);
            // find the level where the walls are located
            Level level = doc.GetElement(element.LevelId) as Level;
            // find the floorplan where the walls are located 
            View sourceView = doc.GetElement(level.FindAssociatedPlanViewId()) as View;
            return sourceView;
        }
        public View GetDestinationView(Document doc, string viewName)
        {
            //  quick filter
            FilteredElementCollector viewCollector = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).OfClass(typeof(ViewPlan));
            // list all view plans
            List<ViewPlan> viewPlans = viewCollector.WhereElementIsNotElementType().OfType<ViewPlan>().ToList();/*Cast<ViewPlan>().ToList();*/
            // query the specific floor plan
            var query = from floorplan in viewPlans
                        where floorplan.ViewType == ViewType.FloorPlan && floorplan.Name == viewName
                        select floorplan;
            // list the specific floor plan
            List<ViewPlan> floorPlans = query.ToList<ViewPlan>();
            // find the objective floor plan
            View destinationView = floorPlans[0];
            return destinationView;
        }

        // （Copy）Translation
        public void TranslateElements(Document doc, ICollection<ElementId> elementIds, View sourceView, View destinationView,
            int sourceX, int sourceY, int destinationX, int destinationY)
        {
            XYZ vector = new XYZ((destinationX - sourceX) * 1.0 / 304.8, (destinationY - sourceY) * 1.0 / 304.8, 0);
            ElementTransformUtils.CopyElements(sourceView, elementIds, destinationView, Transform.CreateTranslation(vector), null);
        }

        // （Copy）Mirroring + Translation
        public void MirrorAndTranslateElements(Document doc, ICollection<ElementId> elementIds, View sourceView, View destinationView,
            int sourceX, int sourceY, int destinationX, int destinationY, string axis_XorY)
        {
            Plane plane = Plane.CreateByNormalAndOrigin(XYZ.BasisY, XYZ.Zero);
            if (axis_XorY == "Y")
                plane = Plane.CreateByNormalAndOrigin(XYZ.BasisX, XYZ.Zero);

            var a = ElementTransformUtils.CopyElements(sourceView, elementIds, destinationView, null, null);
            var b = ElementTransformUtils.MirrorElements(doc, a, plane, true);

            XYZ vector = new XYZ((destinationX - sourceX) * 1.0 / 304.8, (destinationY - (-sourceY)) * 1.0 / 304.8, 0);
            if (axis_XorY == "Y")
                vector = new XYZ((destinationX - (-sourceX)) * 1.0 / 304.8, (destinationY - sourceY) * 1.0 / 304.8, 0);

            ElementTransformUtils.CopyElements(doc, b, vector);
            doc.Delete(a);
            doc.Delete(b);

        }

        // (Copy) counterclockwise Rotation + Translation
        public void RotateAndTranslateElements(Document doc, ICollection<ElementId> elementIds, View sourceView, View destinationView,
            int sourceX, int sourceY, int destinationX, int destinationY, int angle)
        {
            XYZ axis = XYZ.BasisZ;
            XYZ origin = new XYZ(sourceX * 1.0 / 304.8, sourceY * 1.0 / 304.8, 0);
            var a = ElementTransformUtils.CopyElements(sourceView, elementIds, destinationView, Transform.CreateRotationAtPoint(axis, -angle * Math.PI * 1.0 / 180, origin), null);
            XYZ vector = new XYZ((destinationX - sourceX) * 1.0 / 304.8, (destinationY - sourceY) * 1.0 / 304.8, 0);
            ElementTransformUtils.CopyElements(doc, a, vector);
            doc.Delete(a);
        }

        // (Copy) counterclockwise Rotation + Mirroring + Translation
        public void RotateMirrorAndTranslateElements(Document doc, ICollection<ElementId> elementIds, View sourceView, View destinationView,
            int sourceX, int sourceY, int destinationX, int destinationY, int angle, string axis_XorY)
        {
            XYZ axis = XYZ.BasisZ;
            XYZ origin1 = new XYZ(sourceX * 1.0 / 304.8, sourceY * 1.0 / 304.8, 0);
            var a = ElementTransformUtils.CopyElements(sourceView, elementIds, destinationView, Transform.CreateRotationAtPoint(axis, -angle * Math.PI * 1.0 / 180, origin1), null);
            XYZ vector1 = new XYZ((destinationX - sourceX) * 1.0 / 304.8, (destinationY - sourceY) * 1.0 / 304.8, 0);
            var b = ElementTransformUtils.CopyElements(doc, a, vector1);
            doc.Delete(a);

            XYZ origin2 = new XYZ(destinationX * 1.0 / 304.8, destinationY * 1.0 / 304.8, 0);
            Plane plane = Plane.CreateByNormalAndOrigin(XYZ.BasisY, origin2);
            if (axis_XorY == "Y")
                plane = Plane.CreateByNormalAndOrigin(XYZ.BasisX, origin2);
            ElementTransformUtils.MirrorElements(doc, b, plane, true);
            doc.Delete(b);
        }

        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            UIApplication uiApp = commandData.Application;
            UIDocument uiDoc = uiApp.ActiveUIDocument;
            Document doc = uiDoc.Document;

            // please modifiy the path
            string path = "C:\\Users\\xuyin\\OneDrive\\Desktop\\Master_Project\\BIM_Data_Preprocessing\\Geometric_Transformation_Schema.csv";
            List<string> data = CsvFileReader.ReadCSV(path);

            for (int i = 1; i < File.ReadLines(path).Count(); ++i)
            {
                int num = data[i].Split(',').Length;
                string basic_module_source = data[i].Split(',')[0];
                int source_x = int.Parse(data[i].Split(',')[1]);
                int source_y = int.Parse(data[i].Split(',')[2]);

                List<string> ifc_guids = new List<string>();
                string first_str = data[i].Split(',')[3];
                string first_guid = first_str.Substring(3, first_str.Length - 4);
                ifc_guids.Add(first_guid);
                for (int j = 4; j < num - 6; ++j)
                {
                    string str = data[i].Split(',')[j];
                    string guid = str.Substring(2, str.Length - 3);
                    ifc_guids.Add(guid);
                }
                string last_str = data[i].Split(',')[num - 6];
                string last_guid = last_str.Substring(2, last_str.Length - 5);
                ifc_guids.Add(last_guid);

                string basic_module_objective = data[i].Split(',')[num - 5];
                int objective_x = int.Parse(data[i].Split(',')[num - 4]);
                int objective_y = int.Parse(data[i].Split(',')[num - 3]);
                string floor_name = data[i].Split(',')[num - 2];
                string transform = data[i].Split(',')[num - 1];

                ICollection<ElementId> instanceIds = GetElementIds(doc, ifc_guids);

                View sourceView = GetSourceView(doc, instanceIds.ToList()[0]);
                View destinationView = GetDestinationView(doc, floor_name);

                Transaction transaction = new Transaction(doc, "Transform");
                transaction.Start();
                if (transform == "Translation")
                    TranslateElements(doc, instanceIds, sourceView, destinationView, source_x, source_y, objective_x, objective_y);
                if (transform == "Translation + 90-degree Counterclockwise Rotation")
                    RotateAndTranslateElements(doc, instanceIds, sourceView, destinationView, source_x, source_y, objective_x, objective_y, 90);
                if (transform == "Translation + 180-degree Counterclockwise Rotation")
                    RotateAndTranslateElements(doc, instanceIds, sourceView, destinationView, source_x, source_y, objective_x, objective_y, 180);
                if (transform == "Translation + 270-degree Counterclockwise Rotation")
                    RotateAndTranslateElements(doc, instanceIds, sourceView, destinationView, source_x, source_y, objective_x, objective_y, 270);
                if (transform == "Translation + Horizontal Mirror")
                    MirrorAndTranslateElements(doc, instanceIds, sourceView, destinationView, source_x, source_y, objective_x, objective_y, "Y");
                if (transform == "Translation + Vertical Mirror")
                    MirrorAndTranslateElements(doc, instanceIds, sourceView, destinationView, source_x, source_y, objective_x, objective_y, "X");
                if (transform == "Translation + 90-degree Counterclockwise Rotation + Vertical Mirror")
                    RotateMirrorAndTranslateElements(doc, instanceIds, sourceView, destinationView, source_x, source_y, objective_x, objective_y, 90, "X");
                if (transform == "Translation + 90-degree Counterclockwise Rotation + Horizontal Mirror")
                    RotateMirrorAndTranslateElements(doc, instanceIds, sourceView, destinationView, source_x, source_y, objective_x, objective_y, 90, "Y");
                transaction.Commit();
            }

            TaskDialog.Show("Tip", "Transformation is finished");

            return Result.Succeeded;

        }

    }

}
