struct Reading
{
    int value;
    int quality;
};

void reset_reading(int Reading) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-4]
{
    Reading = 0;
}

int main()
{
    struct Reading sample{1, 2};
    reset_reading(sample.value);
    return 0;
}
