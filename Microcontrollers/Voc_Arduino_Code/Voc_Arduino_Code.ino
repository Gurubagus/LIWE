
#define VOLTAGE_1 A1
#define VOLTAGE_2 A2 
#define VOLTAGE_3 A3
#define VOLTAGE_4 A4 
/********************************************************************/
// Data wire is plugged into pin 2 on the Arduino 
#define ONE_WIRE_BUS 2 
/********************************************************************/
#include <OneWire.h> 
#include <DallasTemperature.h>
// Setup a oneWire instance to communicate with any OneWire devices  
// (not just Maxim/Dallas temperature ICs) 
OneWire oneWire(ONE_WIRE_BUS); 
/********************************************************************/
// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);



unsigned long time;

int NUM_SAMPLES = 20;
char clocktime;
char time_t;
float sum1 = 0;     // sum of samples from A1
float sum2 = 0;     // sum of samples from A2
float sum3 = 0;     // sum of samples from A3
float sum4 = 0;     // sum of samples from A4

float R1 = 1000000.00;  
float R2 = 100000.00;

int sample_count = 0;       // current sample number

float V1_ave = 0;
float V2_ave = 0;
float V3_ave = 0;
float V4_ave = 0;

float V1_out = 0;
float V2_out = 0;
float V3_out = 0;
float V4_out = 0;



float V1 = 0.0;       // calculated voltage
float V2 = 0.0;
float V3 = 0.0;       
float V4 = 0.0;



void setup() {
  Serial.begin(9600);
   // Start up the library 
   
 sensors.begin(); 
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
}

void loop(void) 
{
  
while (sample_count < NUM_SAMPLES) 
    {
        sum1 += analogRead(A1);
        sum2 += analogRead(A2);
        sum3 += analogRead(A3);
        sum4 += analogRead(A4);
        sample_count++;
        delay(10);
    }
  V1_ave = (float)sum1 / (float)NUM_SAMPLES;
  V1_out = V1_ave * 5 / 1024;     //2.99796 lähin kalibrointi
  V1 = V1_out / (R2/(R1+R2));

  V2_ave = (float)sum2 / (float)NUM_SAMPLES;
  V2_out = V2_ave * 5 / 1024;     //2.99796 lähin kalibrointi
  V2 = V2_out / (R2/(R1+R2));
  
  V3_ave = (float)sum3 / (float)NUM_SAMPLES;
  V3_out = V3_ave * 5 / 1024;     //2.99796 lähin kalibrointi
  V3 = V3_out / (R2/(R1+R2));
  
  V4_ave = (float)sum4 / (float)NUM_SAMPLES;
  V4_out = V4_ave * 5 / 1024;     //2.99796 lähin kalibrointi
  V4 = V4_out / (R2/(R1+R2));
 
  

  sensors.requestTemperatures(); // Send the command to get temperature readings 
  
  Serial.print(V1);
  Serial.print(",");
  Serial.print(V2);
  Serial.print(",");
  Serial.print(V3);
  Serial.print(",");
  Serial.print(V4);
  Serial.print(",");
  sample_count = 0;
  sum1 = 0;
  sum2 = 0;
  sum3 = 0;
  sum4 = 0;
  Serial.println(sensors.getTempCByIndex(0));// Why "byIndex"?  
   // You can have more than one DS18B20 on the same bus.  
   // 0 refers to the first IC on the wire 
  delay(1000);
}


