char get_char(double value)
{
    return value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-10]
}

int main()
{
    double v = 1.25;
    char c = get_char(v);
    return static_cast<int>(c);
}
