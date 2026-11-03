int value = 0;
int* globalPointer = &value;

int main()
{
    int sum = 0;
    for (*globalPointer = 0; *globalPointer < 10; ++*globalPointer) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-1]
    {
        sum += *globalPointer;
    }
    return sum;
}
