using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Data;
using System.IO;
using System.Globalization;

namespace Crop
{
    public class dt2csv
    {
        public static void ExportDT2csv(DataTable dataDT, string outfn, int itemno, CropInput.TSType selectedType, string unit, string rdmStat, out List<double> rdmValues_tmp)
        {
            rdmValues_tmp = new List<double>();
            // Make sure the directory exists
            System.IO.Directory.CreateDirectory(Path.GetDirectoryName(outfn));

            string csv_fn = outfn.Replace(Path.GetExtension(outfn), ".csv");
            StreamWriter swg = new StreamWriter(csv_fn, false, System.Text.Encoding.ASCII); //Initialise the csv file

            if (selectedType == CropInput.TSType.Envelope)
                dataDT = Process_Envelope(dataDT, 0.25, 0.75);

            if (selectedType == CropInput.TSType.Envelope || selectedType == CropInput.TSType.WeightedTS)
            {
                string csv_header = "Time";

                int noitems = 1;
                //if itemno == -99 then all items are saved to the csv file
                if (itemno == -99)
                {
                    noitems = dataDT.Columns.Count - 1;
                    for (int i = 1; i <= noitems; i++)
                        csv_header = csv_header + "," + dataDT.Columns[i].Caption.ToString();
                }
                else
                    csv_header = csv_header + "," + dataDT.Columns[itemno].Caption.ToString();

                swg.WriteLine(csv_header);

                for (int k = 1; k <= noitems; k++)
                {
                    rdmValues_tmp.Add(0.0);
                }
                
                // add a new line with unit
                if (unit.Length > 0)
                    csv_header = "unit==" + unit;
                swg.WriteLine(csv_header);

                string csv_values = "";

                if (dataDT.Rows.Count > 0)
                {
                    for (int i = 0; i < dataDT.Rows.Count - 1; i++)
                    {
                        DateTime Dato;
                        bool Isdate = DateTime.TryParse(dataDT.Rows[i][0].ToString(), out Dato);

                        csv_values = Dato.ToString("yyyy-MM-dd HH:mm:ss");
                        bool ch_delvalue = false;
                        for (int k = 1; k <= noitems; k++)
                        {
                            int item_count = k;
                            //if (noitems == 1)
                            //   item_count = itemno;

                            ch_delvalue = false;
                            double Value;
                            bool isNum = double.TryParse(dataDT.Rows[i][item_count].ToString(), out Value);
                            if (isNum == false)
                            {
                                Value = -9999d;
                                ch_delvalue = true;
                            }

                            if (ch_delvalue == true)
                                csv_values = csv_values + "," + "-9999";
                            else
                                csv_values = csv_values + "," + Value.ToString("0.000", CultureInfo.InvariantCulture);

                            if (rdmStat == "Cumulative")
                                rdmValues_tmp[k - 1] = rdmValues_tmp[k - 1] + Value;
                            else if(rdmStat == "LastValue")
                                rdmValues_tmp[k - 1] = Value;
                        }
                        swg.WriteLine(csv_values);
                    }
                }
                swg.Close();
            }
            else if (selectedType == CropInput.TSType.Table)
            {

                string csv_header = "description==Monthly " + dataDT.Columns[1].Caption.ToString() + " " + unit;
                swg.WriteLine(csv_header);
                csv_header = "Time,Jan.,Feb.,March,April,May,June,July,Aug.,Sept.,Oct.,Nov.,Dec.,Avg.,Min.,Max.";
                swg.WriteLine(csv_header);

                int noitems = dataDT.Columns.Count - 1;
                if (noitems > 1)
                    dataDT = Process_Envelope(dataDT, 0.25, 0.75); // then we use only the median 

                string csv_values = "";

                double minMonth = Double.MaxValue;
                double maxMonth = Double.MinValue;
                double avgMonth = Double.NaN;
                double avg = Double.NaN;
                double acc = Double.NaN;
                int count = 0;
                int countMonth = 0;

                if (dataDT.Rows.Count > 0)
                {
                    for (int i = 0; i < dataDT.Rows.Count - 1; i++)
                    {
                        DateTime Dato;
                        bool Isdate = DateTime.TryParse(dataDT.Rows[i][0].ToString(), out Dato);

                        if (i == 0)
                        {
                            csv_values = Dato.ToString("yyyy");
                            // add comma if the first year is incomplete
                            //for (int iMonth = 11; iMonth > Dato.Month; iMonth--)
                            //    csv_values += ",";
                            for (int iMonth = 0; iMonth < Dato.Month-1; iMonth++)
                                csv_values += ",";
                        }
                        bool ch_delvalue = false;

                        int k = 1;

                        ch_delvalue = false;
                        double Value;
                        bool isNum = double.TryParse(dataDT.Rows[i][k].ToString(), out Value);
                        if (isNum == false)
                        {
                            Value = -9999d;
                            ch_delvalue = true;
                        }

                        if (ch_delvalue == true)
                            csv_values = csv_values + "," + "-9999";
                        else
                        {
                            if (double.IsNaN(avg))
                                avg = Value;
                            else
                                avg = (avg * count + Value) / (count + 1);
                            if (double.IsNaN(acc))
                                acc = Value;
                            else
                                acc += Value;
                            count++;
                        }

                        // check if next month of next row is different
                        bool bNewMonth = false;
                        bool bNewYear = false;

                        DateTime nextDato = Dato;
                        if (((dataDT.Rows.Count - 2) == i))
                        {
                            bNewYear = true;
                            bNewMonth = true;
                        }
                        else if (DateTime.TryParse(dataDT.Rows[i + 1][0].ToString(), out nextDato))
                        {
                            if (nextDato.Year != Dato.Year)
                            {
                                bNewYear = true;
                                bNewMonth = true;
                            }
                            else if (nextDato.Month != Dato.Month)
                                bNewMonth = true;
                        }

                        if (bNewMonth)
                        {
                            if (Double.IsNaN(avg))
                                csv_values += "," + "-9999";
                            else
                                csv_values += "," + avg.ToString("0.000", CultureInfo.InvariantCulture);


                            // monthly stats
                            minMonth = Math.Min(minMonth, avg);
                            maxMonth = Math.Max(maxMonth, avg);
                            if (double.IsNaN(avgMonth))
                                avgMonth = avg;
                            else
                                avgMonth = (avgMonth * countMonth + avg) / (countMonth + 1);

                            // reset for next month
                            avg = Double.NaN;
                            countMonth++;
                        }
                        if (bNewYear)
                        {
                            // add comma if the last year is incomplete
                            for (int iMonth = Dato.Month; iMonth < 12; iMonth++)
                                csv_values += ",";
                            csv_values += "," + avgMonth.ToString("0.000", CultureInfo.InvariantCulture) + "," + minMonth.ToString("0.000", CultureInfo.InvariantCulture) + "," + maxMonth.ToString("0.000", CultureInfo.InvariantCulture);

                            minMonth = Double.MaxValue;
                            maxMonth = Double.MinValue;
                            avgMonth = Double.NaN;
                            countMonth = 0;
                            swg.WriteLine(csv_values);
                            csv_values = nextDato.ToString("yyyy");
                        }
                    }
                }
                swg.Close();
            }
        }

        public static DataTable Process_Envelope(DataTable DataDT, double lower_perc, double upper_perc)
        {
            //Return the median and lower and upper percentile of a data table

            DataTable DataDT_env = new DataTable();
            DataDT_env.Columns.Add("Date", typeof(DateTime));
            DataDT_env.Columns.Add("Median", typeof(double));
            DataDT_env.Columns.Add((lower_perc * 100).ToString(CultureInfo.InvariantCulture) + " percentile", typeof(double));
            DataDT_env.Columns.Add((upper_perc * 100).ToString(CultureInfo.InvariantCulture) + " percentile", typeof(double));

            //Loop through the data table and calculate the median and the percentile values


            for (int i = 0; i < DataDT.Rows.Count; i++)
            {
                DateTime Dato;
                bool Isdate = DateTime.TryParse(DataDT.Rows[i][0].ToString(), out Dato);
                List<double> tmp_list = new List<double>();
                //Loop across the columns
                for (int j = 1; j < DataDT.Columns.Count; j++)
                {
                    double Value;
                    bool isNum = double.TryParse(DataDT.Rows[i][j].ToString(), out Value);
                    if (isNum == true)
                        if (Value != -9999d)
                            tmp_list.Add(Value);
                }
                if (tmp_list.Count > 0)
                {
                    double median_val = Percentile(tmp_list, 0.5d);
                    double lower_val = Percentile(tmp_list, lower_perc);
                    double upper_val = Percentile(tmp_list, upper_perc);
                    DataDT_env.Rows.Add(new object[] { Dato, median_val, lower_val, upper_val });
                }
            }

            return DataDT_env;
        }

        public static double Percentile(List<double> values, double percentile)
        {
            double[] elements = values.ToArray();

            Array.Sort(elements);
            double realIndex = percentile * (elements.Length - 1);
            int index = (int)realIndex;
            double frac = realIndex - index;
            if (index + 1 < elements.Length)
                return elements[index] * (1 - frac) + elements[index + 1] * frac;
            else
                return elements[index];
        }
    }
}
