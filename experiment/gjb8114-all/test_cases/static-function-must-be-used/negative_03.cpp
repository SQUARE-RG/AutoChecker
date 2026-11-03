namespace calibration
{
static int unused_gain(int sample) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-13]
{
    return sample * 2;
}
}

int main()
{
    return 0;
}
