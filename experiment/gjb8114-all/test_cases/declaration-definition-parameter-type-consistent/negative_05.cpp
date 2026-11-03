int compute(double value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-5]

int compute(float value)
{
    return static_cast<int>(value);
}

int main()
{
    int result = compute(1.5f);
    return result;
}
