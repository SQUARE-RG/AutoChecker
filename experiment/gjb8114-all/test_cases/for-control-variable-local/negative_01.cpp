// Global variable used as the control variable of a for loop.

int loopCounter = 0;

int main()
{
    int sum = 0;
    for (loopCounter = 0; loopCounter < 10; loopCounter++) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-1]
    {
        sum += loopCounter;
    }
    return sum;
}
