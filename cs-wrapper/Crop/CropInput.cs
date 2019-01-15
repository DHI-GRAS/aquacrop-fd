using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Data;
using System.Collections;
using System.IO;
using System.Globalization;

namespace Crop
{
    public class CropInput
    {
        public DataTable Rain_DT = new DataTable();
        public DataTable Temp_DT = new DataTable();
        public DataTable PET_DT = new DataTable();

        public enum Mode { Historic, Forecast, ClimateChange };
        public enum ForecastMode { Climatology, ModelBased};
        public enum TSType { WeightedTS, Envelope, Table };
        public enum ResultItem { Runoff };
        public enum Area { Basin, Subareas };

        public Mode selectedMode;
        public ForecastMode selectedForecastMode = ForecastMode.Climatology; // set defaut value;
        public Area selectedArea;
        public string basinName;
        public string userName;
        public string basinFolder;
        public DateTime plantingDate;
        public string crop;
        public string soil;
        public double area;
        public bool irrigated;
        public double fractioOfRAW;
        public string selectedCCPeriod;
        public string selectedCCRCP;
        public string idRow;

        public void Read_ClimateTS(string prec_ts, string pet_ts, string tempMin_ts, string tempMax_ts, bool ensemble, string climatechange_ts)
        {
            Rain_DT.Columns.Add("Date", typeof(DateTime)); //Date column added

            // *************************
            //If the climate change file exist we extract the monthly change factors in a datatable
            //One column for each member
            DataTable ClimateChange_DT = new DataTable();
            bool climate_ch = false;
            int header_items_ch = 0;
            string[] header_ch = null;

            if (File.Exists(climatechange_ts))
            {
                FileStream fnstr_ch = new FileStream(climatechange_ts, FileMode.Open);
                StreamReader fstr_ch = new StreamReader(fnstr_ch);
                string header_str_ch = fstr_ch.ReadLine(); //Read header line
                header_ch = header_str_ch.Split(new Char[] { ',' });
                header_items_ch = header_ch.GetLength(0) - 1;

                for (int i = 0; i < header_items_ch; i++)
                    ClimateChange_DT.Columns.Add(header_ch[i + 1], typeof(double));

                while (!fstr_ch.EndOfStream)
                {
                    DataRow DT_row = ClimateChange_DT.NewRow();

                    string thestr = fstr_ch.ReadLine();
                    string[] str_arr_ch = thestr.Split(new Char[] { ',' });
                    int month_ch = DateTime.Parse(str_arr_ch[0]).Month; //we dont store the month
                                        
                    for (int i = 0; i < header_items_ch; i++)
                        DT_row[i] = Double.Parse(str_arr_ch[i + 1], NumberStyles.AllowDecimalPoint, System.Globalization.NumberFormatInfo.InvariantInfo);

                    ClimateChange_DT.Rows.Add(DT_row);
                }
                fstr_ch.Close();
                climate_ch = true;
            }
            // *************************

            //Read through the rainfall time series as we let this one decide the dates to be used
            FileStream fnstr;
            fnstr = new FileStream(prec_ts, FileMode.Open);
            StreamReader fstr = new StreamReader(fnstr);
            string header_str = fstr.ReadLine(); //Read header line
            string[] str_arr = header_str.Split(new Char[] { ',' });
            int header_items = str_arr.GetLength(0) - 1;

            if (ensemble == false)
                header_items = 1; //we only read the Data and not the mean column

            for (int i = 0; i < header_items; i++)
            {
                if (climate_ch == false)
                    Rain_DT.Columns.Add(str_arr[i + 1], typeof(double));
                else if (climate_ch == true) //Climate change exist we need to extent with the ensemble values
                {
                    for (int k = 0; k < header_items_ch; k++)
                        Rain_DT.Columns.Add(str_arr[i + 1] + "_" + header_ch[k + 1], typeof(double));
                }
            }

            DateTime thedate = DateTime.MaxValue;
            int diffYear = 0;
            while (!fstr.EndOfStream)
            {
                DataRow DT_row = Rain_DT.NewRow();

                string thestr = fstr.ReadLine();
                str_arr = thestr.Split(new Char[] { ',' });
                thedate = DateTime.Parse(str_arr[0]);
                DT_row[0] = thedate;

                // use first year of CC project

                if (climate_ch == true)
                {
                    if (diffYear == 0)
                    {
                        int year = int.Parse(selectedCCPeriod.Substring(0, 4));
                        diffYear = year - thedate.Year;
                    }
                    DT_row[0] = thedate.AddYears(diffYear);
                }

                for (int i = 0; i < header_items; i++)
                    if (climate_ch == false)
                        DT_row[i + 1] = System.Convert.ToDouble(str_arr[i + 1], CultureInfo.InvariantCulture); //No climate change so we just add the values
                    else if (climate_ch == true)
                    {
                        for (int k = 0; k < header_items_ch; k++)
                        {
                            double scaleFac = System.Convert.ToDouble(ClimateChange_DT.Rows[thedate.Month - 1][k], CultureInfo.InvariantCulture);
                            if (scaleFac == -9999)
                                DT_row[(k + 1) + (i * header_items_ch)] = System.Convert.ToDouble(str_arr[i + 1], CultureInfo.InvariantCulture); // delete value, do not use the scale factor
                            else
                                DT_row[(k + 1) + (i * header_items_ch)] = System.Convert.ToDouble(str_arr[i + 1], CultureInfo.InvariantCulture) * scaleFac; //multiply with the change factor
                        }
                    }
                Rain_DT.Rows.Add(DT_row);
            }
            fstr.Close();

            //************************
            
            //Add the PET values - we use the long term average values
            PET_DT.Columns.Add("Date", typeof(DateTime));
            PET_DT.Columns.Add("PET", typeof(double));
            SetMonthlyMeanValue_DT(ref PET_DT, pet_ts, 1);

            //Add the Temp values - we use the monthly min/max values
            Temp_DT.Columns.Add("Date", typeof(DateTime));
            Temp_DT.Columns.Add("Temp min", typeof(double));
            SetMonthlyMeanValue_DT(ref Temp_DT, tempMin_ts, 1);
            Temp_DT.Columns.Add("Temp max", typeof(double));
            SetMonthlyMeanValue_DT(ref Temp_DT, tempMax_ts, 2);
            //************************
        }

        private void SetValue_DT(DataTable Rain_DT, ref DataTable data_DT, string path_ts)
        {
            // next if/else added to handle hard coded PET value = missing csv file
            if (File.Exists(path_ts))
            {

                //************************
                //we use the long term average values - always assume that we use item 2 in the file
                FileStream fnstr = new FileStream(path_ts, FileMode.Open);
                StreamReader fstr = new StreamReader(fnstr);
                fstr.ReadLine(); //Skip the first line

                List<DateTime> Date_list = new List<DateTime>();
                List<Double> Val_list = new List<double>();

                while (!fstr.EndOfStream)
                {
                    string[] str_arr = fstr.ReadLine().Split(new Char[] { ',' });

                    Date_list.Add(DateTime.Parse(str_arr[0]));
                    Val_list.Add(System.Convert.ToDouble(str_arr[2], CultureInfo.InvariantCulture)); //We always use the mean value
                }
                fstr.Close();

                //Now get values corresponding to the precipitation dates
                DateTime start_date = Date_list[0];
                DateTime end_date = Date_list[Date_list.Count - 1];

                for (int i = 0; i < Rain_DT.Rows.Count; i++)
                {
                    DateTime cur_date = (DateTime)Rain_DT.Rows[i][0];
                    double day_diff = 99999d;
                    int day_counter = -99;

                    bool short_search = false;
                    if ((cur_date < start_date) || (cur_date > end_date)) //If we are looking for a date outside of the data range -> we use month and day for the search
                        short_search = true;

                    for (int j = 0; j < Date_list.Count; j++)
                    {
                        DateTime data_dt = Date_list[j];
                        if (short_search == true)
                            data_dt = new DateTime(cur_date.Year, data_dt.Month, data_dt.Day); //contruct a new date using the current year

                        double ts = Math.Abs((data_dt - cur_date).TotalDays);
                        if (ts < day_diff)
                        {
                            day_diff = ts;
                            day_counter = j;
                        }
                        if (ts == 0d)
                            break;
                    }

                    //Set the value - for now just the closest one - could do an interpolation later
                    DataRow DT_row = data_DT.NewRow();
                    DT_row[0] = cur_date;
                    DT_row[1] = Val_list[day_counter];
                    data_DT.Rows.Add(DT_row);
                }
            }
            //************************
        }

        private void SetMonthlyMeanValue_DT(ref DataTable data_DT, string path_ts, int colNb)
        {
            // next if/else added to handle hard coded PET value = missing csv file
            if (File.Exists(path_ts))
            {
                //************************
                //we use the long term average values - always assume that we use item 2 in the file
                FileStream fnstr = new FileStream(path_ts, FileMode.Open);
                StreamReader fstr = new StreamReader(fnstr);
                fstr.ReadLine(); //Skip the first line

                bool emptyDT = false;
                if (data_DT.Rows.Count == 0)
                    emptyDT = true;
                
                int iRow = 0;

                while (!fstr.EndOfStream)
                {
                    string[] str_arr = fstr.ReadLine().Split(new Char[] { ',' });

                    DateTime cur_date = DateTime.Parse(str_arr[0]);
                    Double curr_val = Double.Parse(str_arr[1], NumberStyles.AllowDecimalPoint, System.Globalization.NumberFormatInfo.InvariantInfo); //We always use the mean value

                    DataRow DT_row;
                    if (emptyDT)
                        DT_row = data_DT.NewRow();
                    else
                        DT_row = data_DT.Rows[iRow];
                    DT_row[colNb] = curr_val;
                    if (emptyDT)
                    {
                        DT_row[0] = cur_date;
                        data_DT.Rows.Add(DT_row);
                    }
                    iRow++;
                }

                fstr.Close();
            }
            else
            {
                Console.WriteLine("  ERROR: TS not found, check: " + path_ts);
                Environment.Exit(0);
            }
            //************************
        }

        public CropInput GetCropInput(string executeFilePath, string sRow)
        {
            // Read parameters from one line of execute.txt
            
            Console.WriteLine("Reading parameters from Execute.txt...");
            
            userName = Path.GetFileName(Path.GetDirectoryName(executeFilePath)); // Name of the last folder
            System.Console.WriteLine("  User name: " + userName);

            basinFolder = executeFilePath.Substring(0, executeFilePath.IndexOf("\\01 Analysis\\AquaCrop\\Results\\")); // basin Name
            System.Console.WriteLine("  Basin folder: " + basinFolder);


            ReadExecuteRow(sRow);

            Console.WriteLine("  Selected area: " + selectedArea.ToString());
            Console.WriteLine("  Basin name: " + basinName);
            Console.WriteLine("  Selected mode: " + selectedMode.ToString());

            // Finds the time series path based on input parameters

            string csvSuffix = selectedArea.ToString() + "_" + basinName + ".csv"; // all csv files end with this string

            string prec_ts;
            string climateChange_ts = ""; // need to set it to empty string

            if (selectedMode == Mode.Forecast) // Mode.Forecast
            {
                if (selectedForecastMode==ForecastMode.ModelBased)
                    prec_ts = System.IO.Path.Combine(basinFolder, @"2_Forecast\SeasonalForecast\WeightedTS\member_") + csvSuffix; 
                else //if (selectedForecastMode==ForecastMode.Climatology)
                    prec_ts = System.IO.Path.Combine(basinFolder, @"1a_CHIRPS\Climatology\WeightedTS\climatology_chirps_") + csvSuffix;
            }
            else // Mode.ClimateChange or Mode.Historic
            {
                prec_ts = System.IO.Path.Combine(basinFolder, @"1a_CHIRPS\WeightedTS\chirps_") + csvSuffix;

                if (selectedMode == Mode.ClimateChange)
                {
                    Console.WriteLine("Applying Climate change scenario: " + selectedCCPeriod + " - " + selectedCCRCP);
                    climateChange_ts = System.IO.Path.Combine(basinFolder, "7_ClimateChange", "data", selectedCCPeriod, "prec", selectedCCRCP, @"WeightedTS\member_") + csvSuffix;
                }
            }

            string tempMin_ts = System.IO.Path.Combine(basinFolder, @"6d_CRU_temp\WeightedTS\tmn_mean_monthly_") + csvSuffix;
            string tempMax_ts = System.IO.Path.Combine(basinFolder, @"6d_CRU_temp\WeightedTS\tmx_mean_monthly_") + csvSuffix;

            string pet_ts = System.IO.Path.Combine(basinFolder, @"6b_CRU_PET\Data\WeightedTS\cru_pet_") + csvSuffix;

            //Read the climate input
            if (!File.Exists(prec_ts))
            {
                Console.WriteLine("  ERROR: rainfall TS not found, check: " + prec_ts);
                Environment.Exit(0);
            }
            if (!File.Exists(tempMin_ts))
            {
                Console.WriteLine("  ERROR: Temperature TS not found, check: " + tempMin_ts);
                Environment.Exit(0);
            }
            
            if (!File.Exists(pet_ts))
            {
                Console.WriteLine("  ERROR: PET TS not found, check: " + pet_ts);
                Environment.Exit(0);
            }
            
            Console.WriteLine("Reading Climate TS");
            this.Read_ClimateTS(prec_ts, pet_ts, tempMin_ts, tempMax_ts, selectedMode == Mode.Forecast, climateChange_ts); // 'ensemble = True' when 'selectedMode == Mode.Forecast'

            Console.WriteLine("Reading Crop parameters");
            
            return this;
        }

        private void ReadExecuteRow(string row)
        {
            // format:
            // areatype=All focus area|area=Volta|climate=Historic|ccscenario=|crop=Maize|soil=Clay|areaha=10|planting=2016-06-01|irrigated=False|fraction=80|id=1

            string[] parameters = row.Split('|');


            foreach (string parameterLong in parameters)
            {
                string paraName = parameterLong.Split('=')[0];
                string paraValue = parameterLong.Split('=')[1];
                if (paraName == "areatype")
                {
                    selectedArea = Area.Basin; // set default value
                    switch (paraValue)
                    {
                        case "Subbasin":
                            selectedArea = Area.Subareas;
                            break;
                        case "All focus area":
                            selectedArea = Area.Basin;
                            break;
                        default:
                            Console.WriteLine("  ERROR: selected area not supported supported (list of supported areas: 'Subbasin', 'All focus area'). Selected area is: " + paraValue);
                            Environment.Exit(0);
                            break;
                    }
                }
                else if (paraName == "areaname")
                {
                    basinName = paraValue;
                }
                else if (paraName == "climate")
                {
                    selectedMode = Mode.Historic; // set defaut value
                    switch (paraValue)
                    {
                        case "Historic":
                            selectedMode = Mode.Historic;
                            break;
                        case "Forecast":
                            selectedMode = Mode.Forecast;
                            break;
                        case "Climate change":
                            selectedMode = Mode.ClimateChange;
                            break;
                        default:
                            Console.WriteLine("  ERROR: selected mode not supported (list of supported mode: 'Historic', 'Forecast', 'Climate change'). Selected mode is: " + paraValue);
                            Environment.Exit(0);
                            break;
                    }
                }
                else if (paraName == "forecast")
                {
                    selectedForecastMode = ForecastMode.Climatology; // set defaut value
                    switch (paraValue)
                    {
                        case "Historical":
                            selectedForecastMode = ForecastMode.Climatology;
                            break;
                        case "ModelBased":
                            selectedForecastMode = ForecastMode.ModelBased;
                            break;
                    }
                }
                else if (paraName == "planting")
                {
                    bool bResult = DateTime.TryParseExact(paraValue, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out plantingDate);
                    
                    //if (!bResult)
                    //{
                        //bResult = DateTime.TryParseExact(paraValue + "-" + DateTime.Now.Year.ToString(), "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out plantingDate);
                    if (!bResult)
                    {
                        Console.WriteLine("  ERROR: the planting date is not correct (format yyyy-MM-dd or MM-dd): " + paraValue);
                        Environment.Exit(0);
                    }
                    //}
                }
                else if (paraName == "crop")
                {
                    crop = paraValue;
                }
                else if (paraName == "soil")
                {
                    soil = paraValue;
                }

                else if (paraName == "areaha")
                {
                    double.TryParse(paraValue, out area);
                }

                else if (paraName == "irrigated")
                {
                    if (!bool.TryParse(paraValue, out irrigated))
                        irrigated = false;
                }
                else if (paraName == "fraction")
                {

                    if (!double.TryParse(paraValue, out fractioOfRAW))
                        fractioOfRAW = 100d;
                }
                else if (paraName == "ccscenario")
                {
                    if (paraValue != null)
                    {
                        // Climate change parameters
                        selectedCCPeriod = "2016-2035"; // set defaut value
                        selectedCCRCP = "rcp45"; // set defaut value}
                    }
                }
                else if (paraName == "id")
                {
                    idRow = paraValue;
                }
            }
        }
    }
}

