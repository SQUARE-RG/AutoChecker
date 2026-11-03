float narrow()
{
    double value = 3.25;
    return value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-10]
}

int main()
{
    float result = narrow();
    (void)result;
    return 0;
}
