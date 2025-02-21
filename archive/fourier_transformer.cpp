#include <stdlib.h>
#include <math.h>
#include <fftw3.h>
#include "csv.hpp"

#include <string>
#include <sys/resource.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <unistd.h>
#define p_len 8388608
#define c_len 536870912
using namespace csv;
fftw_complex channel[p_len];
fftw_complex out[p_len];

std::vector<std::string> split(const std::string& str, char delimiter) {
    std::vector<std::string> tokens;
    std::stringstream ss(str);
    std::string token;
    std::cout << "Input string: " << str << std::endl;

    while (std::getline(ss, token, delimiter)) {
        tokens.push_back(token);
    }

    return tokens;
}

int main(void) {
    bool complete = false;
    
    for (int pi=0; pi < c_len/p_len; pi++){
        
        CSVReader reader("recording_25082024.csv");
        CSVRow row;
        fftw_plan p;


        //make array of this sice
        

        std::string lasttime_s = "";
        float lasttime = 0;
        float newtime = 0;
        float delta = 0;
        std::vector<std::string> parts;
        char delimiter = '.';
        float expected_delta = 0.001;
        int_fast64_t i = 0;
        int_fast64_t ai = 0;
        std::vector<std::string> splitstring;
        std::vector<std::string> tokens;
        std::string token;
        std::stringstream ss;
        std::string startTime = "";
        std::string endTime = "";
        for (auto& row: reader) {
            // Note: Can also use index of column with [] operator
            ai = i-pi*p_len;
            if (ai < 0){
                i++;
                continue;
            }
            if (ai== p_len){
                break;
            }
            channel[ai][0] =  0.0001331253868*(row["Dev1-18"].get<double>());
            
            
            lasttime_s = (row["System_Time"].get<std::string>());
            if (ai==0){
                startTime = lasttime_s;
            }
            endTime = lasttime_s;
            //printf("%s", lasttime_s.c_str());
            //printf("\n");
            /*ss = std::stringstream(lasttime_s);
            //ss << lasttime_s;
            while (std::getline(ss, token, delimiter)) {
                tokens.push_back(token);
            }
            lasttime_s = tokens[1];
            tokens.pop_back();
            tokens.pop_back();
            newtime = std::stof(lasttime_s)/1000000;
            delta = expected_delta-(newtime-lasttime);
            double second = 1;
            delta = std::modf(delta,&second);
            if (abs(delta) > 0.0000001){
                printf("%f",delta);
                printf("\n");
            }
            lasttime = newtime;*/


            //lasttime = splitstring
            i++;
        }
        while (ai<p_len){
            ai = i-pi*p_len;
            channel[ai][0] = 0;
            i++;
            complete = true;
        }


        p = fftw_plan_dft_1d(p_len, channel, out, FFTW_FORWARD, FFTW_ESTIMATE);
        fftw_execute(p);
        /*for (j = 0; j < p_len; j++){
            printf("freq: %3d %+9.5f %+9.5f I\n", j, out[i][0], out[i][1]);
        }*/
        fftw_destroy_plan(p);

        fftw_cleanup();
        //put this in a new csv
        std::string oname = "fftw_output_c2_";
        char pre = '0';
        int shift = pi;
        while (shift >= 10){
            pre+=1;
            shift -= 10;
        }
        oname = oname + pre + (char)(shift + '0');
        oname = oname + ".csv";
        std::ofstream outFile(oname);
        if (!outFile.is_open()) {
            std::cerr << "Failed to open file for writing." << std::endl;
            fftw_free(out);
            return 1;
        }
        outFile << "Index,Real,Imaginary\n";
        for (int j = 0; j < p_len; ++j) {
            outFile << j << "," << out[j][0] << "," << out[j][1] << "\n";
        }
        outFile.close();
        oname = "meta_" + oname;

        std::ofstream outFile2(oname);
        if (!outFile2.is_open()) {
            std::cerr << "Failed to open file for writing." << std::endl;
            fftw_free(out);
            return 1;
        }
        outFile2 << startTime << "\n";
        outFile2 << endTime;
        outFile2.close();
        if (complete){
            printf("complete!");
            break;
        }

    }
    
    return 0;
}
int main_2(void) {
    using namespace csv;
    CSVReader reader("recording_25082024.csv");
    CSVRow row;
    double col_len=0;
    for (auto& row: reader) {
        // Note: Can also use index of column with [] operator
        col_len++;
    }
    printf("%f",col_len);
    return 0;
}
