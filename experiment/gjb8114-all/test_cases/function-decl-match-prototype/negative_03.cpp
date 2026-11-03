// negative_03.cpp
// Multi-parameter prototype and definition have a parameter-name mismatch.
int multiply(int x, int y); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-14]

int main()
{
    int a = 3;
    int b = 4;
    return multiply(a, b);
}

int multiply(int x, int count)
{
    return x * count;
}
