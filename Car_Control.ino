// RC Car MCU Control 
// Authur: Haoran Hong
 

#include <Servo.h>  //Servo library
Servo servo;  // create servo object to control servo 
Servo motor;  // create servo object to control motor   

//Initialise pins with name           
int straight  =  3; 
int lightleft  =  4;
int lightright  =  5;
int hardleft = 6;
int hardright =  7;
const int trigPin = 11;
const int echoPin = 12;
int led = 13;
long duration;
int distance;

// Setup 
void setup() 
{    
  servo.attach(9);  // attaches the servo on pin 9 to the servo object 
  motor.attach(10); // attaches the esc on pin 10 to the motor object 
  
  // Set pin input/output  
  pinMode(straight,INPUT);
  pinMode(lightleft,INPUT);
  pinMode(lightright,INPUT);
  pinMode(hardleft,INPUT);
  pinMode(hardright,INPUT);
  pinMode(led, OUTPUT);
  pinMode(trigPin, OUTPUT); 
  pinMode(echoPin, INPUT); 
} 

// Steering fucntion
void steer (){
  
  if (digitalRead(straight) == HIGH){   // high read on input pin                      
      servo.write(80);  // ouput PWM with angle 80           
      delay(100); // delay to allow servo movement   
    }       
    
  if (digitalRead(lightleft) == HIGH){                      
      servo.write(65);           
      delay(100);   
    }      
    
  if (digitalRead(lightright) == HIGH){                      
      servo.write(95);           
      delay(100);   
    }
    
  if (digitalRead(hardleft) == HIGH){                      
      servo.write(50);           
      delay(100);   
    }      
    
  if (digitalRead(hardright) == HIGH){                      
      servo.write(110);           
      delay(100);   
    } 
}  

// Collision Detection Function
void collision (){
  
    motor.write(90);  // drive motor
    digitalWrite(trigPin, LOW);   // set trigger pin low
    delayMicroseconds(2);
    
    digitalWrite(trigPin, HIGH);  // set trigger pin high with slight delay 
    delayMicroseconds(10);
    
    digitalWrite(trigPin, LOW);   // reset trigger to low
    
    duration = pulseIn(echoPin, HIGH);  // echo pin, returns the sound wave 
                                        //travel time(ms)
   
    distance = (duration*0.034)/2;    // distance calculation, d=t*v(cm)
    
    // if distance < 4cm stop motor for 5 seconds 
    if (distance < 4){    
      motor.write(100);
      digitalWrite(led, HIGH);  // led indicator 
      delay(5000);   
    }
    else{
      digitalWrite(led, LOW);
    }
} 
  
// Main loop
void loop() 
{ 
  steer();  // steering function
  
  collision();  // collision detection function
} 


