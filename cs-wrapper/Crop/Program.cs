using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Crop
{
    class Program
    {
        static void Main(string[] args)
        {
            System.Console.WriteLine("Starting the Crop program...");
            //# arg0: path to execute.txt file
            string executeTxtPath = args[0];
            System.Console.WriteLine("  Execute txt file: " + executeTxtPath);

            if (!File.Exists(executeTxtPath))
            {
                System.Console.WriteLine("  ERROR: execute.txt file does not exist");
                Environment.Exit(0);
            }

            string[] lines = System.IO.File.ReadAllLines(executeTxtPath);
            if (lines.Length < 1)
            {
                System.Console.WriteLine("  ERROR: execute.txt file does not contain any rows");
                Environment.Exit(0);
            }

            string userFolderPath = Path.GetDirectoryName(executeTxtPath);

            //Add the Progress.log file as well             
            string _path_progress = userFolderPath + "//Progress.log";

            int counterMembers = 0;
            int counterLines = 0;
            foreach (string iLine in lines)
            {
                File.WriteAllText(_path_progress, counterLines.ToString() + "/" + lines.Length.ToString());
                CropEngine cropEngine = new CropEngine();
                cropEngine.CropInput = cropEngine.CropInput.GetCropInput(executeTxtPath, iLine);

                // Call the NAM engine
                System.Console.WriteLine("Running Crop engine...");

                
                cropEngine.engine(userFolderPath);

                // Store the results to csv files
                System.Console.WriteLine("Saving Crop results...");
                int nbMembers;
                Results.WriteResults(counterMembers, out nbMembers, cropEngine);
                counterMembers+=nbMembers;
                counterLines++;
            }
            File.WriteAllText(_path_progress, lines.Length.ToString() + "/" + lines.Length.ToString());
            System.Console.WriteLine("End of Crop program.");
        }

        private void _writeToProgressFile(string folderPath, string str)
        {
            

            // write to the file
            
        }
    }
}
