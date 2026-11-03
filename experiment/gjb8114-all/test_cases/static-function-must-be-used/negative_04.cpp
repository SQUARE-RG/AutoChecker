static int convert(int value)
{
    return value + 1;
}

int main()
{
    return convert(5) == 6 ? 0 : 1;
}

static double convert(double value) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-13]
{
    return value + 1.0;
}
