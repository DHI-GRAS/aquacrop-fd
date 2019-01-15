using System;
using System.Collections.Generic;
using System.Data;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Crop
{
    public class CropEngine
    {
        public CropInput CropInput = new CropInput();
        private DataTable DTResults = new DataTable();
        public DataTable DTIrrDemand = new DataTable();
        public DataTable DTBiomassRel = new DataTable();
        public DataTable DTRain = new DataTable();
        public DataTable DTET = new DataTable();
        public DataTable DTDepletion = new DataTable();
        public DataTable DTStage = new DataTable();
        public DataTable DTRootDepth = new DataTable();
        public DataTable DTYield = new DataTable();
        public DataTable DTBiomass = new DataTable();
        public DataTable DTHi = new DataTable();
        public DataTable DTWpet = new DataTable();
        public DataTable DTRelCropTransp = new DataTable();

        private string newLine = ""; //"\n";

        internal void engine(string userFolder)
        {
            string workingDir = System.IO.Path.Combine(userFolder, @"Execute\ACsaV60Nr17042017");


            //- Rename the path to input files in PRO file to be compatible with working directory
            string projectFilePath = workingDir + "\\LIST\\Template.PRO";
            UpdatePathInTextFile(projectFilePath, workingDir);

            //- Set Crop, Climate, Soil and sowing date from Spreadsheet

            //-- read all parameters (for 1 sim or as a list)

            //   this is already done in before calling engine.

            //-- crop: change path to the CRO file based on selection
            ChangeFileNameAccordingToType(projectFilePath, CropInput.crop.ToString(), ".CRO");
            int growingSeasonInDays = GetGrowingSeasonLength(workingDir, CropInput.crop.ToString());

            //-- soil: change path to the SOL file based on selection
            ChangeFileNameAccordingToType(projectFilePath, CropInput.soil.ToString(), ".SOL");

            //-- Sowing date: change the date in the template file

            //TODO separate start date and planting date
            SetStartAndEndDate(projectFilePath, CropInput.plantingDate, CropInput.plantingDate, growingSeasonInDays);

            //-- Irrigation: change the date in the template file, and Allowable depletion of RAW (in %)

            // TODO add this to the execute txt file
            bool irrigation = CropInput.irrigated;
            double fracOfRAW = CropInput.fractioOfRAW;
            SetIrrigation(projectFilePath, workingDir, irrigation, fracOfRAW);

            //-- climate model: read values from TS and change climate.plu and Climate.ETo files
            // check number of member in the ensemble TS
            DataTable rainfallTS = CropInput.Rain_DT;

            // TODO add a check here
            //if(rainfallTS == None):
            //    UpdateStatus('ERROR: Rainfall TS cannot be found. Please check the path.')
            //    raise AssertionError

            int nbRainfallMembers = rainfallTS.Columns.Count - 1;

            for (int iMember = 0; iMember < nbRainfallMembers; iMember++)
            {
                WriteClimateData(workingDir, rainfallTS, iMember, CropInput.PET_DT, CropInput.Temp_DT);

                //- Run the Aquacrop plugin
                System.Console.WriteLine("\tSimulation " + iMember.ToString() + "/" + nbRainfallMembers.ToString() + " members has started...");
                bool returncode = RunAquaCropPlugin(workingDir);

                if (returncode)
                {
                    //- Read results
                    System.Console.WriteLine("\tImport of result of last simulation...");
                    ImportResultsToDT(workingDir, "Template", iMember);
                }
            }
        }

        private void ImportResultsToDT(string workingDir, string projectFileName, int iMember)
        {
            //string resultsFilePath = workingDir + "\\OUTP\\" + projectFileName + "PROseason.OUT";
            string resultsFilePath = workingDir + "\\OUTP\\" + projectFileName + "PROday.OUT";
            int header_items_ch = 0;
            string[] header_ch = null;

            DataRow DTIrrDemand_row = null;
            DataRow DTYieldRel_row = null;
            DataRow DTRain_row = null;
            DataRow DTET_row = null;
            DataRow DTDepletion_row = null;
            DataRow DTStage_row = null;
            DataRow DTRootDepth_row = null;
            DataRow DTYield_row = null;
            DataRow DTBiomass_row = null;
            DataRow DTHi_row = null;
            DataRow DTWpet_row = null;
            DataRow DTRelCropTransp_row = null;

            int IrrDemandIndex = 7;
            int YieldRelIndex = 42;
            int RainIndex = 6;
            int ETIndex = 21;
            //int DepletionIndex = -1; // being calculated
            int StageIndex = 4;
            int RootDepthIndex = 24;
            int YieldIndex = 41;
            int BiomassIndex = 39;
            int HiIndex = 40;
            int Wpetindex = 43;
            int RelCropTranspIndex = 19;

            if (File.Exists(resultsFilePath))
            {
                FileStream fnstr_ch = new FileStream(resultsFilePath, FileMode.Open);
                StreamReader fstr_ch = new StreamReader(fnstr_ch);
                string header_str_ch = fstr_ch.ReadLine(); // Read header line
                header_str_ch = fstr_ch.ReadLine(); // blank
                header_str_ch = fstr_ch.ReadLine(); // this line contains the headers
                header_ch = header_str_ch.Split(new Char[] { ' ' }, System.StringSplitOptions.RemoveEmptyEntries);
                header_items_ch = header_ch.GetLength(0) - 1;

                if (iMember == 0)
                {
                    DTIrrDemand.Columns.Add("Date", typeof(DateTime));
                    DTBiomassRel.Columns.Add("Date", typeof(DateTime));
                    DTRain.Columns.Add("Date", typeof(DateTime));
                    DTET.Columns.Add("Date", typeof(DateTime));
                    DTDepletion.Columns.Add("Date", typeof(DateTime));
                    DTStage.Columns.Add("Date", typeof(DateTime));
                    DTRootDepth.Columns.Add("Date", typeof(DateTime));
                    DTYield.Columns.Add("Date", typeof(DateTime));
                    DTBiomass.Columns.Add("Date", typeof(DateTime));
                    DTHi.Columns.Add("Date", typeof(DateTime));
                    DTWpet.Columns.Add("Date", typeof(DateTime));
                    DTRelCropTransp.Columns.Add("Date", typeof(DateTime));
                }
                DTIrrDemand.Columns.Add(header_ch[IrrDemandIndex] + (iMember+1).ToString(), typeof(double)); // Irr
                DTBiomassRel.Columns.Add(header_ch[YieldRelIndex] + (iMember + 1).ToString(), typeof(double)); // Brelative
                DTRain.Columns.Add(header_ch[RainIndex] + (iMember + 1).ToString(), typeof(double)); // Rain
                DTET.Columns.Add(header_ch[ETIndex] + (iMember + 1).ToString(), typeof(double)); // ET
                DTDepletion.Columns.Add("Dr" + (iMember + 1).ToString(), typeof(double)); // Dr 
                DTStage.Columns.Add(header_ch[StageIndex] + (iMember + 1).ToString(), typeof(double)); // Stage
                DTRootDepth.Columns.Add(header_ch[RootDepthIndex] + (iMember + 1).ToString(), typeof(double)); // Z
                DTYield.Columns.Add(header_ch[YieldIndex] + (iMember + 1).ToString(), typeof(double)); // Yield
                DTBiomass.Columns.Add(header_ch[BiomassIndex] + (iMember + 1).ToString(), typeof(double)); // Biomass
                DTHi.Columns.Add(header_ch[HiIndex] + (iMember + 1).ToString(), typeof(double)); // HI
                DTWpet.Columns.Add(header_ch[Wpetindex] + (iMember + 1).ToString(), typeof(double)); // WPet: ET Water Productivity for yield part (kg/m^3)
                DTRelCropTransp.Columns.Add(header_ch[RelCropTranspIndex] + (iMember + 1).ToString(), typeof(double)); // Tr/Trx: Relative crop transpiration (%)

                header_str_ch = fstr_ch.ReadLine(); // units

                int iTS = 0;
                while (!fstr_ch.EndOfStream)
                {
                    if (iMember == 0)
                    {
                        DTIrrDemand_row = DTIrrDemand.NewRow();
                        DTYieldRel_row = DTBiomassRel.NewRow();
                        DTRain_row = DTRain.NewRow();
                        DTET_row = DTET.NewRow();
                        DTDepletion_row = DTDepletion.NewRow();
                        DTStage_row = DTStage.NewRow();
                        DTRootDepth_row = DTRootDepth.NewRow();
                        DTYield_row = DTYield.NewRow();
                        DTBiomass_row = DTBiomass.NewRow();
                        DTHi_row = DTHi.NewRow();
                        DTWpet_row = DTWpet.NewRow();
                        DTRelCropTransp_row = DTRelCropTransp.NewRow();
                    }
                    else
                    {
                        DTIrrDemand_row = DTIrrDemand.Rows[iTS];
                        DTYieldRel_row = DTBiomassRel.Rows[iTS];
                        DTRain_row = DTRain.Rows[iTS];
                        DTET_row = DTET.Rows[iTS];
                        DTDepletion_row = DTDepletion.Rows[iTS];
                        DTStage_row = DTStage.Rows[iTS];
                        DTRootDepth_row = DTRootDepth.Rows[iTS];
                        DTYield_row = DTYield.Rows[iTS];
                        DTBiomass_row = DTBiomass.Rows[iTS];
                        DTHi_row = DTHi.Rows[iTS];
                        DTWpet_row = DTWpet.Rows[iTS];
                        DTRelCropTransp_row = DTRelCropTransp.Rows[iTS];
                    }
                    string thestr = fstr_ch.ReadLine();
                    string[] str_arr_ch = thestr.Split(new Char[] { ' ' }, System.StringSplitOptions.RemoveEmptyEntries);
                    DateTime dato = new DateTime(int.Parse(str_arr_ch[2]), int.Parse(str_arr_ch[1]), int.Parse(str_arr_ch[0])); // for "PROday.OUT" 
                    
                    DateTime prevDato;
                    if (iTS > 0)
                    {
                        prevDato = (DateTime)DTIrrDemand.Rows[iTS - 1][0];

                        if (dato < prevDato)
                            break;
                    }
                    DTIrrDemand_row[0] = dato;
                    DTIrrDemand_row[iMember + 1] = System.Convert.ToDouble(str_arr_ch[IrrDemandIndex], CultureInfo.InvariantCulture);
                    
                    DTYieldRel_row[0] = dato;
                    DTYieldRel_row[iMember + 1] = System.Convert.ToDouble(str_arr_ch[YieldRelIndex], CultureInfo.InvariantCulture);
                    
                    DTRain_row[0] = dato;
                    DTRain_row[iMember + 1] = System.Convert.ToDouble(str_arr_ch[RainIndex], CultureInfo.InvariantCulture);

                    DTET_row[0] = dato;
                    DTET_row[iMember + 1] = System.Convert.ToDouble(str_arr_ch[ETIndex], CultureInfo.InvariantCulture);

                    // Dr = Wr(FC) – Wr
                    DTDepletion_row[0] = dato;
                    DTDepletion_row[iMember + 1] = System.Convert.ToDouble(str_arr_ch[49], CultureInfo.InvariantCulture) - System.Convert.ToDouble(str_arr_ch[47], CultureInfo.InvariantCulture);

                    DTStage_row[0] = dato;
                    DTStage_row[iMember + 1] = System.Convert.ToDouble(str_arr_ch[StageIndex], CultureInfo.InvariantCulture);

                    DTRootDepth_row[0] = dato;
                    DTRootDepth_row[iMember + 1] = System.Convert.ToDouble(str_arr_ch[RootDepthIndex], CultureInfo.InvariantCulture);

                    DTYield_row[0] = dato;
                    DTYield_row[iMember + 1] = System.Convert.ToDouble(str_arr_ch[YieldIndex], CultureInfo.InvariantCulture);

                    DTBiomass_row[0] = dato;
                    DTBiomass_row[iMember + 1] = System.Convert.ToDouble(str_arr_ch[BiomassIndex], CultureInfo.InvariantCulture);

                    DTHi_row[0] = dato;
                    DTHi_row[iMember + 1] = System.Convert.ToDouble(str_arr_ch[HiIndex], CultureInfo.InvariantCulture);

                    DTWpet_row[0] = dato;
                    DTWpet_row[iMember + 1] = System.Convert.ToDouble(str_arr_ch[Wpetindex], CultureInfo.InvariantCulture);

                    DTRelCropTransp_row[0] = dato;
                    DTRelCropTransp_row[iMember + 1] = System.Convert.ToDouble(str_arr_ch[RelCropTranspIndex], CultureInfo.InvariantCulture);

                    if (iMember == 0)
                    {
                        DTIrrDemand.Rows.Add(DTIrrDemand_row);
                        DTBiomassRel.Rows.Add(DTYieldRel_row);
                        DTRain.Rows.Add(DTRain_row);
                        DTDepletion.Rows.Add(DTDepletion_row);
                        DTET.Rows.Add(DTET_row);
                        DTStage.Rows.Add(DTStage_row);
                        DTRootDepth.Rows.Add(DTRootDepth_row);
                        DTYield.Rows.Add(DTYield_row);
                        DTBiomass.Rows.Add(DTBiomass_row);
                        DTHi.Rows.Add(DTHi_row);
                        DTWpet.Rows.Add(DTWpet_row);
                        DTRelCropTransp.Rows.Add(DTRelCropTransp_row);
                    }

                    iTS = iTS + 1;
                }
                fstr_ch.Close();
            }
            else
            {
                System.Console.WriteLine("  ERROR: PROday.OUT result file does not exist");
                Environment.Exit(0);
            }
        }
        
        private void WriteClimateData(string workingDir, DataTable rainfallTS, int iMember, DataTable PETTS, DataTable TempDT)
        {
            string PLUfilePath = workingDir + "\\DATA\\" + "Climate.PLU";
            string ETofilePath = workingDir + "\\DATA\\" + "Climate.ETo";
            string TempfilePath = workingDir + "\\DATA\\" + "Climate.TMP";

            //---TODO resample to daily time step...

            // update rainfall
            int nbTimeSteps = rainfallTS.Rows.Count;
            
            string[] PLUfileLinesNew = new string[nbTimeSteps + 8]; // = PLUfileLines;

            //---write the header of PLU file
            DateTime startTSDate;
            bool Isdate = DateTime.TryParse(rainfallTS.Rows[0][0].ToString(), out startTSDate);

            PLUfileLinesNew[0] = "Rainfall data from ts: " + rainfallTS.TableName + newLine;
            PLUfileLinesNew[1] = "    1  : Daily records (1=daily, 2=10-daily and 3=monthly data)" + newLine;
            PLUfileLinesNew[2] = "    " + startTSDate.Day.ToString() + "  : First day of record (1, 11 or 21 for 10-day or 1 for months)" + newLine; // # month
            PLUfileLinesNew[3] = "    " + startTSDate.Month.ToString() + "  : First month of record" + newLine;
            PLUfileLinesNew[4] = "    " + startTSDate.Year.ToString() + "  : First year of record (1901 if not linked to a specific year)" + newLine; //# year
            PLUfileLinesNew[5] = newLine;
            PLUfileLinesNew[6] = "  Total Rain (mm)" + newLine;
            PLUfileLinesNew[7] = "=======================" + newLine;

            //---get the data from time series
            
            for (int iTS = 0; iTS < nbTimeSteps; iTS++)
            {
                string currData = ((double)rainfallTS.Rows[iTS][iMember + 1]).ToString("0.00", CultureInfo.InvariantCulture);
                PLUfileLinesNew[8 + iTS] = currData + newLine;
            }

            System.IO.File.WriteAllLines(PLUfilePath, PLUfileLinesNew);

            // update ETo
            //---write the header of ETo file
            nbTimeSteps = 12; // PETTS.Rows.Count; //write only 1 year of data
            
            string[] ETofileLinesNew = new string[370 + 8]; // = ETofileLines;

            DateTime.TryParse(PETTS.Rows[0][0].ToString(), out startTSDate);

            ETofileLinesNew[0] = "Pot ET data from CRU" + newLine;
            ETofileLinesNew[1] = "    1  : Daily records (1=daily, 2=10-daily and 3=monthly data)" + newLine;
            ETofileLinesNew[2] = "    1  : First day of record (1, 11 or 21 for 10-day or 1 for months)" + newLine; // # month
            ETofileLinesNew[3] = "    " + startTSDate.Month.ToString() + "  : First month of record" + newLine;
            ETofileLinesNew[4] = "    1901  : First year of record (1901 if not linked to a specific year)" + newLine; // year
            ETofileLinesNew[5] = newLine;
            ETofileLinesNew[6] = "  PET (mm)" + newLine;
            ETofileLinesNew[7] = "=======================" + newLine;

            //---get the data from time series
            int iRow = 8;
            for (int iTS = 0; iTS < nbTimeSteps; iTS++)
            {
                string currData = ((double)PETTS.Rows[iTS][1]).ToString("00.0", CultureInfo.InvariantCulture);
                int nbDayInMonth = DateTime.DaysInMonth(startTSDate.AddMonths(iTS).Year,startTSDate.AddMonths(iTS).Month);
                for (int iDay = 0; iDay < nbDayInMonth; iDay++)
                {
                    ETofileLinesNew[iRow] = currData + newLine;
                    iRow++;
                }
            }

            System.IO.File.WriteAllLines(ETofilePath, ETofileLinesNew);

            // update Temp Min/max
            //---write the header of TMP file
            nbTimeSteps = 12;

            string[] TmpfileLinesNew = new string[nbTimeSteps + 8];

            DateTime.TryParse(TempDT.Rows[0][0].ToString(), out startTSDate);

            TmpfileLinesNew[0] = "mean monthly data from TS: " + TempDT.TableName + newLine;
            TmpfileLinesNew[1] = "    3  : Daily records (1=daily, 2=10-daily and 3=monthly data)" + newLine;
            TmpfileLinesNew[2] = "    1  : First day of record (1, 11 or 21 for 10-day or 1 for months)" + newLine; // # month
            TmpfileLinesNew[3] = "    " + startTSDate.Month.ToString() + "  : First month of record" + newLine;
            TmpfileLinesNew[4] = "    1901  : First year of record (1901 if not linked to a specific year)" + newLine; // year
            TmpfileLinesNew[5] = newLine;
            TmpfileLinesNew[6] = "  Tmin (C)   TMax (C)" + newLine;
            TmpfileLinesNew[7] = "=======================" + newLine;

            //---get the data from time series

            for (int iTS = 0; iTS < nbTimeSteps; iTS++)
            {
                string currData = ((double)TempDT.Rows[iTS][1]).ToString("00.0", CultureInfo.InvariantCulture);
                TmpfileLinesNew[8 + iTS] = "      " + currData;
                currData = ((double)TempDT.Rows[iTS][2]).ToString("00.0", CultureInfo.InvariantCulture);
                TmpfileLinesNew[8 + iTS] += "      " + currData + newLine;
            }

            System.IO.File.WriteAllLines(TempfilePath, TmpfileLinesNew);

        }

        void SetIrrigation(string projectFilePath, string workingDir, bool irrigation, double fracOfRAW)
        {
            string lineNone = "   (None)";
            string dataFolder = "\\DATA\\";
            string irrigationFile = "Irrigation.IRR";

            // update project file
            string[] lines = System.IO.File.ReadAllLines(projectFilePath);
            string[] newLines = lines;

            for (int iLine = 0; iLine < lines.Length; iLine++)
            {
                string lineout = "";
                if (iLine == 46)
                {
                    if (irrigation)
                        lineout = "   " + irrigationFile + newLine;
                    else
                        lineout = lineNone + newLine;
                    newLines[iLine] = lineout;
                }
                else if (iLine == 47)
                {
                    if (irrigation)
                        lineout = "   " + workingDir + dataFolder + newLine;
                    else
                        lineout = lineNone + newLine;
                    newLines[iLine] = lineout;
                }
            }
            System.IO.File.WriteAllLines(projectFilePath, newLines);


            // update irrgation file
            string irrgationFilePath = workingDir + "\\DATA\\" + irrigationFile;

            lines = System.IO.File.ReadAllLines(irrgationFilePath);
            newLines = lines;

            newLines[5] = "  " + fracOfRAW.ToString("00") + "     : Allowable depletion of RAW (%)";

            System.IO.File.WriteAllLines(irrgationFilePath, newLines);
        }

        private void SetStartAndEndDate(string projectFilePath, DateTime startSimDate, DateTime plantingDate, int growingSeasonInDays)
        {
            DateTime endDate = startSimDate + TimeSpan.FromDays(growingSeasonInDays);

            string[] lines = System.IO.File.ReadAllLines(projectFilePath);
            string[] newLines = lines;

            for (int iLine = 0; iLine < lines.Length; iLine++)
            {
                string lineout = "";
                if (iLine == 2) // First day of simulation period
                {
                    lineout = "  ";
                    lineout = lineout + ConvertDateToNumber(startSimDate);
                    lineout = lineout + "         : First day of simulation period - ";
                    lineout = lineout + startSimDate.ToString("dd MM yyyy");
                    lineout = lineout + newLine;
                    newLines[iLine] = lineout;
                }
                else if (iLine == 3) // Last day of simulation period -    
                {
                    lineout = "  ";
                    lineout = lineout + ConvertDateToNumber(endDate);
                    lineout = lineout + "         : Last day of simulation period - ";
                    lineout = lineout + endDate.ToString("dd MM yyyy");
                    lineout = lineout + newLine;
                    newLines[iLine] = lineout;
                }
                else if (iLine == 4) // First day of cropping period -    
                {
                    lineout = "  ";
                    lineout = lineout + ConvertDateToNumber(plantingDate);
                    lineout = lineout + "         : First day of cropping period - ";
                    lineout = lineout + plantingDate.ToString("dd MM yyyy");
                    lineout = lineout + newLine;
                    newLines[iLine] = lineout;
                }
                else if (iLine == 5) // Last day of cropping period -    
                {
                    lineout = "  ";
                    lineout = lineout + ConvertDateToNumber(endDate);
                    lineout = lineout + "         : Last day of cropping period - ";
                    lineout = lineout + endDate.ToString("dd MM yyyy");
                    lineout = lineout + newLine;
                    newLines[iLine] = lineout;
                }

            }

            System.IO.File.WriteAllLines(projectFilePath, newLines);
        }

        private string ConvertDateToNumber(DateTime dateAsDate)
        {

            // 1. Subtract 1901 from the year
            double dateAsNumber = dateAsDate.Year - 1901;
            // 2. Multiply by 365.25
            dateAsNumber = dateAsNumber * 365.25;
            // 3.    According to the month add:

            double[] monthConvertion = { 0, 31, 59.25, 90.25, 120.25, 151.25, 181.25, 212.25, 243.25, 273.25, 304.25, 334.25 };
            dateAsNumber = dateAsNumber + monthConvertion[dateAsDate.Month - 1]; // monthConvertion is zero-based

            // 4. Add the number of the day within the month
            dateAsNumber = dateAsNumber + dateAsDate.Day;

            return (Math.Truncate(dateAsNumber)).ToString();
        }
        //def TestDateConvertion():
        //    dateAsDate = datetime.date(1990,3,22)
        //    dateAsNumber = ConvertDateToNumber(dateAsDate) # should return 32588
        //    pass;


        private int GetGrowingSeasonLength(string workingDir, string crop)
        {
            string cropFilePath = workingDir + "\\DATA\\" + crop + ".CRO";
            int growingSeasonLength = 365; // in case the length is not read properly

            if (!System.IO.File.Exists(cropFilePath))
            {
                //System.Exception('ERROR: cannot find crop file for: '+crop)
            }
            string[] lines = System.IO.File.ReadAllLines(cropFilePath);

            char[] spliter = { ':' };
            string[] text = lines[54].Split(':'); // Calendar Days: from transplanting to maturity

            growingSeasonLength = int.Parse(text[0]);
            return growingSeasonLength;
        }

        private void ChangeFileNameAccordingToType(string projectFilePath, string fileName, string fileType)
        {
            string textToFind = fileType;

            string[] lines = System.IO.File.ReadAllLines(projectFilePath);
            string[] newLines = lines;

            for (int i = 0; i < lines.Length; i++)
            {
                string lineout = lines[i];
                if (lineout.Contains(textToFind))
                    lineout = "   " + fileName + fileType + newLine;
                newLines[i] = lineout;
            }
            System.IO.File.WriteAllLines(projectFilePath, newLines);
        }

        private void UpdatePathInTextFile(string projectFilePath, string workingDir)
        {
            string textToFind = "\\DATA\\";
            string[] lines = System.IO.File.ReadAllLines(projectFilePath);

            string[] newLines = lines;

            for (int i = 0; i < lines.Length; i++)
            {
                string lineout = lines[i];
                if (lineout.Contains(textToFind))
                    lineout = "   " + workingDir + textToFind + newLine;
                newLines[i] = lineout;
            }
            System.IO.File.WriteAllLines(projectFilePath, newLines);
        }

        private bool RunAquaCropPlugin(string workingDir)
        {
            string pluginfullpath = workingDir + "\\ACsaV60.exe";
            // it will not run if there is space in the path, so '"' are added
            //pluginfullpath = '"' + pluginfullpath + '"';

            try
            {
                // Start the process with the info we specified.
                // Call WaitForExit and then the using statement will close.
                using (Process exeProcess = Process.Start(pluginfullpath))
                {
                    // wait for 5 sec if process has not completed it's because Aquacrop failed
                    exeProcess.WaitForExit(5000);
                    if (!exeProcess.HasExited)
                        exeProcess.Kill();

                    return true;
                }
            }
            catch
            {
                // Log error.
                return false;
            }
        }
    }
}
