long double convert_value()
{
    double value = 2.5;
    return value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-10]
}

int main()
{
    long double result = convert_value();
    return (result > 0.0L) ? 0 : 1;
}
