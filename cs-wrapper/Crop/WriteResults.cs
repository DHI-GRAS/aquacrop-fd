using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Globalization;

namespace Crop
{
    public class Results
    {
        public static void WriteResults(int ensembleIndex, out int nbMembers, CropEngine cropEngine)
        {
            CropInput input = cropEngine.CropInput;

            nbMembers = cropEngine.DTRain.Columns.Count - 1; // do not count time column

            // for Forecast and climate change 2 type of TS will be saved: WeightedTS and Envelope
            // the lines below will create a list 'selectedTypes' which has:
            //   1 element for historic: so results will only be saved as WeightedTS
            //   2 elements for Forecast and CC: so results will be saved as WeightedTS and Envelope
            CropInput.TSType[] selectedTypes;// = new TSTypeList<TSType>();
            if (input.selectedMode == CropInput.Mode.Historic)
            {
                selectedTypes = new CropInput.TSType[2];
                selectedTypes[0] = CropInput.TSType.WeightedTS;
                selectedTypes[1] = CropInput.TSType.Table;
            }
            else
            {
                selectedTypes = new CropInput.TSType[3];
                selectedTypes[0] = CropInput.TSType.WeightedTS;
                selectedTypes[1] = CropInput.TSType.Envelope;
                selectedTypes[2] = CropInput.TSType.Table;
            }

            string csvSuffix = input.selectedArea.ToString() + "_" + input.basinName + "_" + input.idRow + ".csv"; // all csv files end with this string


            foreach (CropInput.TSType selectedType in selectedTypes)
            {
                // path to the output folder
                string outfolder = System.IO.Path.Combine(input.basinFolder, @"01 Analysis\AquaCrop\Results", input.userName, selectedType.ToString());

                string selectedModeToString = input.selectedMode.ToString();
                if (input.selectedMode == CropInput.Mode.ClimateChange) selectedModeToString = "Climate change"; // workaround to handle the space in this type (web expects a space in the file name)
                // Demand
                List<double> rdmValue_Demand;
                string outfn = Path.Combine(outfolder, selectedModeToString + "_CropWaterDemand_" + csvSuffix);
                dt2csv.ExportDT2csv(cropEngine.DTIrrDemand, outfn, -99, selectedType, "mm", "Cumulative", out rdmValue_Demand);
                System.Console.WriteLine("\tDemand csv saved at: " + outfn);
                // Biomass relative
                List<double> rdmValue_BiomassRel;
                outfn = Path.Combine(outfolder, selectedModeToString + "_BiomassRel_" + csvSuffix);
                dt2csv.ExportDT2csv(cropEngine.DTBiomassRel, outfn, -99, selectedType, "%", "LastValue", out rdmValue_BiomassRel);
                System.Console.WriteLine("\tBiomass rel csv saved at: " + outfn);
                // Rain
                List<double> rdmValue_Rain;
                outfn = Path.Combine(outfolder, selectedModeToString + "_Rain_" + csvSuffix);
                dt2csv.ExportDT2csv(cropEngine.DTRain, outfn, -99, selectedType, "mm", "Cumulative", out rdmValue_Rain);
                System.Console.WriteLine("\tRain csv saved at: " + outfn);
                // ET
                List<double> rdmValue_ET;
                outfn = Path.Combine(outfolder, selectedModeToString + "_ET_" + csvSuffix);
                dt2csv.ExportDT2csv(cropEngine.DTET, outfn, -99, selectedType, "mm", "Cumulative", out rdmValue_ET);
                System.Console.WriteLine("\tET csv saved at: " + outfn);
                // Wr
                List<double> rdmValue_Depletion;
                outfn = Path.Combine(outfolder, selectedModeToString + "_Depletion_" + csvSuffix);
                dt2csv.ExportDT2csv(cropEngine.DTDepletion, outfn, -99, selectedType, "mm", "None", out rdmValue_Depletion);
                System.Console.WriteLine("\tDepletion csv saved at: " + outfn);
                // Stage
                List<double> rdmValue_Stage;
                outfn = Path.Combine(outfolder, selectedModeToString + "_Stage_" + csvSuffix);
                dt2csv.ExportDT2csv(cropEngine.DTStage, outfn, -99, selectedType, "Stage", "None", out rdmValue_Stage);
                System.Console.WriteLine("\tStage csv saved at: " + outfn);
                // Root depth
                List<double> rdmValue_RootDepth;
                outfn = Path.Combine(outfolder, selectedModeToString + "_RootDepth_" + csvSuffix);
                dt2csv.ExportDT2csv(cropEngine.DTRootDepth, outfn, -99, selectedType, "m", "LastValue", out rdmValue_RootDepth);
                System.Console.WriteLine("\tRoot depth csv saved at: " + outfn);
                // Yield
                List<double> rdmValue_Yield;
                outfn = Path.Combine(outfolder, selectedModeToString + "_Yield_" + csvSuffix);
                dt2csv.ExportDT2csv(cropEngine.DTYield, outfn, -99, selectedType, "ton/ha", "LastValue", out rdmValue_Yield);
                System.Console.WriteLine("\tYield csv saved at: " + outfn);
                // Biomass
                List<double> rdmValue_DTBiomass;
                outfn = Path.Combine(outfolder, selectedModeToString + "_Biomass_" + csvSuffix);
                dt2csv.ExportDT2csv(cropEngine.DTBiomass, outfn, -99, selectedType, "ton/ha", "LastValue", out rdmValue_DTBiomass);
                System.Console.WriteLine("\tBiomass csv saved at: " + outfn);
                // Harvest index
                List<double> rdmValue_Hi;
                outfn = Path.Combine(outfolder, selectedModeToString + "_HarvestIndex_" + csvSuffix);
                dt2csv.ExportDT2csv(cropEngine.DTHi, outfn, -99, selectedType, "%", "LastValue", out rdmValue_Hi);
                System.Console.WriteLine("\tHarvest index csv saved at: " + outfn);
                // Wpet
                List<double> rdmValue_Wpet;
                outfn = Path.Combine(outfolder, selectedModeToString + "_Wpet_" + csvSuffix);
                dt2csv.ExportDT2csv(cropEngine.DTWpet, outfn, -99, selectedType, "kg/m^3", "LastValue", out rdmValue_Wpet);
                System.Console.WriteLine("\tRoot depth csv saved at: " + outfn);
                // RelCropTransp
                List<double> rdmValue_RelCropTransp;
                outfn = Path.Combine(outfolder, selectedModeToString + "_RelCropTransp_" + csvSuffix);
                dt2csv.ExportDT2csv(cropEngine.DTRelCropTransp, outfn, -99, selectedType, "%", "LastValue", out rdmValue_RelCropTransp);
                System.Console.WriteLine("\tRel Crop Transp csv saved at: " + outfn);

                
                if (selectedType == CropInput.TSType.WeightedTS)
                {
                    List<string> rdmValue_all = new List<string>();
                    for (int j = 0; j < nbMembers; j++)
                    {
                        string row = rdmValue_Demand[j].ToString(CultureInfo.InvariantCulture) + ",";
                        row += rdmValue_BiomassRel[j].ToString(CultureInfo.InvariantCulture) + ",";
                        row += rdmValue_Rain[j].ToString(CultureInfo.InvariantCulture) + ",";
                        row += rdmValue_ET[j].ToString(CultureInfo.InvariantCulture) + ",";
                        row += rdmValue_Yield[j].ToString(CultureInfo.InvariantCulture) + ",";
                        row += rdmValue_DTBiomass[j].ToString(CultureInfo.InvariantCulture) + ",";
                        row += rdmValue_Hi[j].ToString(CultureInfo.InvariantCulture) + ",";
                        row += rdmValue_Wpet[j].ToString(CultureInfo.InvariantCulture) + ",";
                        row += rdmValue_RelCropTransp[j].ToString(CultureInfo.InvariantCulture);
                        rdmValue_all.Add(row);
                    }

                    WriteRDMValues(ensembleIndex, cropEngine, rdmValue_all);
                }
            }
        }

        private static void WriteRDMValues(int ensembleIndex, CropEngine cropEngine, List<string> rdmValue)
        {
            // prepare header for the RDM spreadsheet
            CropInput input = cropEngine.CropInput;
            string rdm_csv_fn = System.IO.Path.Combine(input.basinFolder, @"01 Analysis\AquaCrop\Results", input.userName, "RDM_Crop.csv");
            
            StreamWriter swg;
            
            // prepare rdm csv file
            if (ensembleIndex == 0)
            {
                swg = new StreamWriter(rdm_csv_fn, false, System.Text.Encoding.ASCII); //Initialise the csv file
                string csv_row = "Ensemble index,Climate ensemble indicator (),Soil type,Crop type,Planting date,Irr demand (mm),Biomass (%),Rain (mm),ET (mm),Yield (ton/ha),Biomass (ton/ha), Harvest index (%),Wpet (kg/m^3), Rel Crop Transp (%)";
                swg.WriteLine(csv_row);
            }
            else
                swg = new StreamWriter(rdm_csv_fn, true, System.Text.Encoding.ASCII); //Initialise the csv file

            // write columns with input to rdm, csv file

            // 1. Ensemble index
            // 2. Climate ensemble index
            // 3. soil type
            // 4. Crop type
            // 5. Planting date
            // 6. Irrigation demand (mm), 
            // 7. Biomass (%),
            // 8. Rain (mm),
            // 9. ET (mm),
            // 10.Yield (ton/ha),
            // 11.Biomass (ton/ha),
            // 12.Harvest index (%),
            // 13.Wpet (kg/m^3),
            // 14.Rel Crop Transp (%)

            // Get last index from the file
            // Increment and write as many lines as members
            int nbRainfallMembers = cropEngine.DTRain.Columns.Count - 1;
            for (int iMember = 0; iMember < nbRainfallMembers; iMember++)
            {
                string csv_row = (ensembleIndex + iMember).ToString() + ",";
                csv_row += iMember.ToString() + ",";
                csv_row += cropEngine.CropInput.soil.ToString() + ",";
                csv_row += cropEngine.CropInput.crop.ToString() + ",";
                csv_row += cropEngine.CropInput.plantingDate.ToString() + ",";
                csv_row += rdmValue[iMember];
                swg.WriteLine(csv_row);
            }

            swg.Close();
        }
    }
}
