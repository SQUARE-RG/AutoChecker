double scale(double factor);

int main()
{
    double (*fn)(double) = scale;
    float ratio = 1.5f;
    return static_cast<int>(fn(ratio)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-2]
}

double scale(double factor)
{
    return factor * 2.0;
}
